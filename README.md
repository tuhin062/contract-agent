# Contract Agent

A professional contract management and generation platform with AI-powered validation and workflow automation.

## 🚀 Features

- **Contract Generation**: Create contracts from templates with AI assistance
- **Smart Validation**: Automatic compliance checking and risk assessment
- **Proposal Management**: Upload and review vendor proposals
- **Template Library**: Pre-configured templates for common contract types
- **Role-Based Access**: Different permissions for Users, Reviewers, and Admins
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Shadcn/UI** component library
- **React Query** for data fetching
- **React Router** for navigation
- **TanStack Table** for data tables

### Backend (Planned)
- Python FastAPI
- PostgreSQL database
- JWT authentication
- PDF processing

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Git

### Frontend Setup

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

## 🎯 User Roles

1. **Regular User**: Create contracts, upload proposals, view status
2. **Legal Reviewer**: Validate contracts, approve/reject submissions
3. **Admin**: Manage users, create templates, configure settings

## 📁 Project Structure

```
Contract Agent/
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utilities and helpers
│   │   └── types/         # TypeScript type definitions
│   ├── public/            # Static assets
│   └── package.json
└── backend/              # Backend API (in development)
```

## 🌟 Key Features

### Contract Management
- Create contracts from templates
- View all contracts with advanced filtering
- Download contracts as PDF
- Track contract status and approvals

### Validation System
- AI-powered risk detection
- Clause comparison against standards
- Compliance percentage scoring
- Detailed validation reports

### Template System
- Professional contract templates
- Customizable fields
- Template versioning
- Usage analytics

### Responsive Design
- Mobile-optimized sidebar with hamburger menu
- Scrollable data tables on small screens
- Touch-friendly interface
- Consistent experience across devices

## 🎨 UI Components

All UI components built with:
- Consistent design system
- Smooth animations and transitions
- Accessibility considerations
- Dark mode support

## 📄 Documentation

- **User Journey Guide**: See `User_Journey_Guide.md` for detailed user workflows
- **GitHub Upload Guide**: See `GitHub_Upload_Guide.md` for deployment instructions

## 🔄 Development Status

✅ **Completed:**
- Frontend UI with all pages
- Component library
- Responsive design
- Mock data integration
- User journey documentation

🚧 **In Progress:**
- Backend API development
- Real-time notifications
- Advanced filtering
- PDF generation

## 🤝 Contributing

This is a personal project. For suggestions or issues, please open an issue.

## 📝 License

Private project - All rights reserved

## 👤 Author

Tuhin Dutta

## 🙏 Acknowledgments

- Shadcn/UI for component library
- Tailwind CSS for styling system
- React community for excellent tools
