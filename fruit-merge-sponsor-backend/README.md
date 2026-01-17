# Fruit Merge Sponsor Backend

Gas sponsorship backend for the Fruit Merge game on Sui blockchain.

## Overview

This backend service sponsors gas fees for users playing the Fruit Merge game, allowing them to interact with the Sui blockchain without needing SUI tokens for gas.

## Features

- **Gas Sponsorship**: Sponsor gas fees for user transactions
- **Transaction Signing**: Sign transactions as the gas payer
- **Transaction Execution**: Submit transactions to the Sui network
- **Health Monitoring**: Health check endpoint for monitoring

## Setup

### Prerequisites

- Node.js 18+ 
- npm or pnpm

### Installation

```bash
cd fruit-merge-sponsor-backend
npm install
```

### Configuration

Create a `.env` file in the `fruit-merge-sponsor-backend` directory:

```env
SPONSOR_SECRET_KEY=suiprivkey1qzkejytknake27tl58q5ymnvdz63e6zq8cp69x0a3ng89rsvdamuz9kwvqn
SUI_NETWORK=https://fullnode.testnet.sui.io:443
FRONTEND_URL=http://localhost:5173
PORT=3000
```

**Environment Variables:**

- `SPONSOR_SECRET_KEY`: Your sponsor account private key (suiprivkey format or base64)
- `SUI_NETWORK`: Sui network URL (testnet or mainnet)
- `FRONTEND_URL`: Your frontend URL for CORS configuration
- `PORT`: Server port (default: 3000)

### Running the Server

**Development Mode:**
```bash
npm run dev
```

**Production Mode:**
```bash
npm run build
npm start
```

## API Endpoints

### Health Check

**GET** `/health`

Returns server status and sponsor account information.

**Response:**
```json
{
  "status": "ok",
  "sponsor": "0x438b067c...",
  "network": "https://fullnode.testnet.sui.io:443",
  "timestamp": "2026-01-17T03:24:23.510Z"
}
```

### Sponsor Transaction

**POST** `/api/sponsor`

Adds gas payment and sponsor signature to a transaction.

**Request Body:**
```json
{
  "transactionBytes": [1, 2, 3, ...],
  "userAddress": "0x..."
}
```

**Response:**
```json
{
  "sponsoredTransactionBytes": [1, 2, 3, ...],
  "sponsorSignature": "...",
  "sponsorAddress": "0x..."
}
```

### Execute Transaction

**POST** `/api/execute`

Submits the transaction to the Sui network with both user and sponsor signatures.

**Request Body:**
```json
{
  "transactionBytes": [1, 2, 3, ...],
  "userSignature": "...",
  "sponsorSignature": "..."
}
```

**Response:**
```json
{
  "digest": "...",
  "effects": {...},
  "objectChanges": [...]
}
```

## Sponsor Account

The sponsor account loaded:
- **Address**: `0x438b067c7ad8673897d826d5800621aeba1d9016f5c0db4d0f97550bfd9059da`
- **Key Scheme**: ed25519
- **Network**: Testnet

**⚠️ Important**: Keep the `SPONSOR_SECRET_KEY` secure and never commit it to version control.

## Architecture

```
Frontend (User Wallet)
    ↓
    1. Build transaction (no gas)
    ↓
Backend (/api/sponsor)
    ↓
    2. Add gas payment (sponsor's SUI)
    3. Sign as gas payer
    ↓
Frontend
    ↓
    4. User signs transaction
    ↓
Backend (/api/execute)
    ↓
    5. Submit to Sui with both signatures
    ↓
Sui Network ✅
```

## Security Considerations

1. **Rate Limiting**: Consider adding rate limiting to prevent abuse
2. **Authentication**: Add user authentication if needed
3. **Gas Budget**: Monitor sponsor account balance
4. **Transaction Validation**: Validate transactions before sponsoring
5. **CORS**: Configure CORS properly for your frontend domain

## Monitoring

The server logs important events:
- ✅ Sponsor account loaded
- 📡 Sponsorship requests
- 💰 Sponsor balance
- ⚠️ Low balance warnings
- ❌ Errors and failures

## Troubleshooting

**Error: "Sponsor account out of gas"**
- Fund the sponsor account with more SUI tokens

**Error: "Failed to load sponsor keypair"**
- Check that `SPONSOR_SECRET_KEY` is correctly formatted
- Ensure it's in `suiprivkey` format or base64

**CORS errors**
- Update `FRONTEND_URL` in `.env` to match your frontend

## License

MIT
