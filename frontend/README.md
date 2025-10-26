# Legal Advisory System v5.0 - Frontend

Modern React frontend for the Legal Advisory System.

## Features

- 💬 Real-time chat interface
- 📊 Calculation results display
- ❓ Follow-up questions
- 📈 Progress indicators
- 🎨 Modern, responsive design
- ⚡ Fast and lightweight

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Update VITE_API_URL in .env with your backend URL

# Start development server
npm run dev

# Open http://localhost:3000
```

### Build for Production

```bash
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file:

```bash
# Your Railway backend URL
VITE_API_URL=https://your-app.railway.app
```

## Deployment

### Netlify

See [NETLIFY_DEPLOYMENT.md](../NETLIFY_DEPLOYMENT.md) for detailed instructions.

Quick deploy:
1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Add environment variable: `VITE_API_URL`
5. Deploy!

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **CSS3** - Styling
- **Fetch API** - HTTP requests

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx        # Main application component
│   ├── App.css        # Application styles
│   ├── main.jsx       # Entry point
│   └── index.css      # Global styles
├── public/            # Static assets
├── index.html         # HTML template
├── package.json       # Dependencies
├── vite.config.js     # Vite configuration
└── netlify.toml       # Netlify configuration
```

## Usage

1. The app automatically creates a session on load
2. Type your legal query in the input field
3. View responses with calculations and breakdowns
4. Answer follow-up questions to refine results
5. See progress bar indicating completeness

## Example Queries

- "I need costs for a High Court default judgment for $50,000"
- "What are the costs for a 3-day contested trial in District Court?"
- "Summary judgment in Magistrates Court for $20,000"

## Troubleshooting

**Cannot connect to API:**
- Check VITE_API_URL in .env
- Verify backend is running
- Check CORS settings in backend

**Build fails:**
- Run `npm install` to ensure dependencies are installed
- Check Node version (requires 18+)

## License

© 2025 Legal Advisory System v5.0
