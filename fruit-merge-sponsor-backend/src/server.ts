import 'dotenv/config'
import express from 'express'
import cors from 'cors'
import { Transaction } from '@mysten/sui/transactions'
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519'
import { SuiClient } from '@mysten/sui/client'
import { fromBase64 } from '@mysten/sui/utils'

const app = express()

// CORS - Allow your frontend
app.use(cors({
  origin: process.env.FRONTEND_URL || '*',
  credentials: true
}))

app.use(express.json({ limit: '10mb' }))

// Initialize sponsor keypair from environment
const SPONSOR_SECRET_KEY = process.env.SPONSOR_SECRET_KEY
if (!SPONSOR_SECRET_KEY) {
  throw new Error('SPONSOR_SECRET_KEY environment variable is required')
}

let sponsorKeypair: Ed25519Keypair
try {
  // Support both base64 and suiprivkey formats
  let secretKeyBytes: Uint8Array
  
  if (SPONSOR_SECRET_KEY.startsWith('suiprivkey')) {
    // suiprivkey format: "suiprivkey" + bech32 encoded (flag byte + 32 bytes secret + checksum)
    // We need to decode and extract the 32-byte secret key (skip first flag byte, ignore last 4 checksum bytes)
    const base64Part = SPONSOR_SECRET_KEY.replace('suiprivkey', '')
    const decoded = fromBase64(base64Part)
    // Extract 32 bytes starting from index 1 (skip flag byte)
    secretKeyBytes = decoded.slice(1, 33)
  } else {
    // Plain base64 encoded 32-byte secret key
    secretKeyBytes = fromBase64(SPONSOR_SECRET_KEY)
  }
  
  sponsorKeypair = Ed25519Keypair.fromSecretKey(secretKeyBytes)
  console.log('✅ Sponsor account loaded:', sponsorKeypair.toSuiAddress())
} catch (error) {
  console.error('❌ Failed to load sponsor keypair:', error)
  throw error
}

const SUI_NETWORK = process.env.SUI_NETWORK || 'https://fullnode.testnet.sui.io:443'
const client = new SuiClient({ url: SUI_NETWORK })

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    sponsor: sponsorKeypair.toSuiAddress(),
    network: SUI_NETWORK,
    timestamp: new Date().toISOString()
  })
})

// Sponsor endpoint - Add gas payment and sign
app.post('/api/sponsor', async (req, res) => {
  try {
    const { transactionBytes, userAddress } = req.body

    if (!transactionBytes || !userAddress) {
      return res.status(400).json({ 
        error: 'Missing required fields: transactionBytes, userAddress' 
      })
    }

    console.log('📡 Sponsorship request from:', userAddress)
    
    // 1. Reconstruct transaction from bytes
    const txBytesArray = Array.isArray(transactionBytes) 
      ? new Uint8Array(transactionBytes)
      : new Uint8Array(Object.values(transactionBytes))
    
    const tx = Transaction.fromKind(txBytesArray)
    
    // 2. Set user as sender
    tx.setSender(userAddress)
    
    // 3. Set sponsor as gas payer
    const sponsorAddress = sponsorKeypair.toSuiAddress()
    tx.setGasOwner(sponsorAddress)
    
    // 4. Get gas coins for sponsor
    const gasCoins = await client.getCoins({
      owner: sponsorAddress,
      coinType: '0x2::sui::SUI',
      limit: 10,
    })
    
    if (!gasCoins.data.length) {
      console.error('❌ Sponsor account has no SUI for gas')
      return res.status(500).json({ 
        error: 'Sponsor account out of gas. Please contact administrator.' 
      })
    }

    // Check sponsor balance
    const totalBalance = gasCoins.data.reduce((sum, coin) => sum + BigInt(coin.balance), 0n)
    console.log(`💰 Sponsor balance: ${Number(totalBalance) / 1_000_000_000} SUI`)

    if (totalBalance < 100_000_000n) { // Less than 0.1 SUI
      console.warn('⚠️ Sponsor balance is low!')
    }
    
    // 5. Set gas payment (use first coin)
    tx.setGasPayment([{
      objectId: gasCoins.data[0].coinObjectId,
      version: gasCoins.data[0].version,
      digest: gasCoins.data[0].digest,
    }])
    
    // 6. Build transaction with gas
    const sponsoredTxBytes = await tx.build({ client })
    
    // 7. Sponsor signs the transaction
    const { signature: sponsorSignature } = await sponsorKeypair.signTransaction(
      sponsoredTxBytes
    )
    
    console.log('✅ Transaction sponsored successfully')
    
    // 8. Return sponsored transaction to frontend
    res.json({
      sponsoredTransactionBytes: Array.from(sponsoredTxBytes),
      sponsorSignature,
      sponsorAddress,
    })
    
  } catch (error: any) {
    console.error('❌ Sponsorship error:', error)
    res.status(500).json({ 
      error: error.message || 'Failed to sponsor transaction',
      details: error.toString()
    })
  }
})

// Execute endpoint - Submit transaction to Sui network
app.post('/api/execute', async (req, res) => {
  try {
    const { transactionBytes, userSignature, sponsorSignature } = req.body

    if (!transactionBytes || !userSignature || !sponsorSignature) {
      return res.status(400).json({ 
        error: 'Missing required fields: transactionBytes, userSignature, sponsorSignature' 
      })
    }

    console.log('🚀 Executing sponsored transaction...')
    
    const txBytesArray = Array.isArray(transactionBytes)
      ? new Uint8Array(transactionBytes)
      : new Uint8Array(Object.values(transactionBytes))
    
    // Execute with both signatures
    const result = await client.executeTransactionBlock({
      transactionBlock: txBytesArray,
      signature: [userSignature, sponsorSignature],
      options: {
        showEffects: true,
        showObjectChanges: true,
      }
    })
    
    if (result.effects?.status?.status === 'success') {
      console.log('✅ Transaction executed:', result.digest)
    } else {
      console.error('❌ Transaction failed:', result.effects?.status?.error)
    }
    
    res.json(result)
    
  } catch (error: any) {
    console.error('❌ Execution error:', error)
    res.status(500).json({ 
      error: error.message || 'Failed to execute transaction',
      details: error.toString()
    })
  }
})

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', err)
  res.status(500).json({ error: 'Internal server error' })
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════╗
║  🎮 Fruit Merge Sponsor Backend       ║
╠════════════════════════════════════════╣
║  Port:     ${PORT}                     ║
║  Network: ${SUI_NETWORK.includes('testnet') ? 'Testnet' : 'Mainnet'}              ║
║  Sponsor: ${sponsorKeypair.toSuiAddress().slice(0, 8)}...  ║
╚════════════════════════════════════════╝
  `)
})
