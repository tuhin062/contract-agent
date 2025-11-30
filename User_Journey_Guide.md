# Contract Agent - User Journey Guide

> **For Non-Technical Users:** This guide explains who can use the system and what they can do, step by step.

---

## 👥 User Roles in the System

The Contract Agent application has **3 types of users** (roles):

### 1️⃣ **Regular User** (Employee/Staff)
- Can create and view contracts
- Can upload proposals
- **Cannot** approve or validate contracts
- **Cannot** access admin settings

### 2️⃣ **Legal Reviewer** (Legal Team/Manager)
- Can do everything a Regular User can do
- **Can also** approve or reject contracts
- **Can also** validate contracts for compliance
- **Cannot** access admin settings

### 3️⃣ **Admin** (System Administrator)
- Can do everything Legal Reviewers can do
- **Can also** manage users and settings
- **Can also** create and edit templates
- **Full access** to all features

---

## 🚶 User Journey Flows

### Role 1: Regular User Journey

**What they want to do:** Create a contract, upload proposals, check contract status

#### Step-by-Step Flow:

**1. Login**
- User enters email and password
- Clicks "Login" button
- System shows Dashboard

**2. View Dashboard**
- User sees 4 cards at the top:
  - Total Contracts (how many they have)
  - Pending Approvals (waiting for review)
  - Active Contracts (approved and running)
  - Flagged Validations (contracts with issues)
- User sees recent contracts list
- User sees quick action buttons

**3. Generate a New Contract (Option A)**
- User clicks **"Generate Contract"** button from Dashboard
- User sees contract generation page
- User fills in details:
  - Contract title
  - Contract type (NDA, Employment, Vendor Agreement, etc.)
  - Party names
  - Dates
  - Other required information
- User clicks **"Generate"** button
- System creates contract
- User sees success message
- Contract appears in "Contracts" list with status "Draft"

**4. Upload a Proposal (Option B)**
- User clicks **"Upload Proposal"** icon in sidebar
- User sees upload screen
- User clicks "Browse" to select PDF file
- User fills in proposal details:
  - Project name
  - Vendor name
  - Timeline
  - Budget
- User clicks **"Upload"** button
- System saves proposal
- User sees success message
- Proposal appears in "Proposals" list

**5. View All Contracts**
- User clicks **"Contracts"** in sidebar
- User sees table with all their contracts:
  - Contract name
  - Type
  - Status (Draft, Pending Approval, Active, Expired)
  - Parties involved
  - Start and end dates
- User can:
  - Sort by clicking column headers
  - Search using search box
  - Filter by status
  - Click on a contract to see details

**6. View Contract Details**
- User clicks on a contract name
- User sees detailed contract page with:
  - PDF preview of contract
  - Contract information (parties, dates, value)
  - Current status
  - Validation results (if checked)
  - Action buttons
- User can:
  - Download PDF
  - Print contract
  - See who needs to approve it

**7. View Templates**
- User clicks **"Templates"** in sidebar
- User sees list of available contract templates
- User can:
  - Click on template to see details
  - Use template to create new contract
  - Preview template before using

**8. Check Validation Status**
- User goes to contract details
- User sees "Validation" section
- If contract was validated, user sees:
  - Risk level (Low, Medium, High, Critical)
  - List of issues found
  - Suggestions to fix issues
- User **cannot** approve contract (only Legal Reviewer can)

---

### Role 2: Legal Reviewer Journey

**What they want to do:** Review contracts, approve/reject them, validate for legal compliance

#### Step-by-Step Flow:

**All steps from Regular User, PLUS:**

**9. Validate a Contract**
- User clicks **"Validate Contract"** in sidebar
- User sees validation page
- User uploads contract PDF OR selects existing contract
- User clicks **"Validate"** button
- System checks contract against legal standards
- User sees validation results:
  - Overall risk score
  - Compliance percentage
  - List of risks found (with severity colors):
    - 🔴 Critical (red)
    - 🟠 High (orange)
    - 🟡 Medium (yellow)
    - 🔵 Low (blue)
  - Side-by-side comparison of clauses
  - Suggested fixes
- User can:
  - Expand each risk to see details
  - See affected contract sections
  - Download validation report

**10. Approve or Reject Contracts**
- User goes to **"Contracts"** page
- User filters to see "Pending Approval" contracts
- User clicks on contract to review
- User sees contract details and validation results
- User has two buttons:
  - **"Approve"** button (green)
  - **"Reject"** button (red)
- When user clicks **"Approve"**:
  - System asks for confirmation
  - User can add approval notes
  - Contract status changes to "Active"
  - Creator gets notification
- When user clicks **"Reject"**:
  - System asks for reason
  - User types rejection reason
  - Contract goes back to "Draft"
  - Creator gets notification with feedback

**11. Review Proposals**
- User clicks **"Proposals"** in sidebar
- User sees all submitted proposals
- User can:
  - Click on proposal to see details
  - See key information (budget, timeline, vendor)
  - View proposal PDF
  - Accept or reject proposal
  - Add comments

---

### Role 3: Admin Journey

**What they want to do:** Manage users, create templates, configure system

#### Step-by-Step Flow:

**All steps from Legal Reviewer, PLUS:**

**12. Access Admin Panel**
- User clicks **"Admin"** in sidebar
- User sees admin dashboard with tabs:
  - User Management
  - Templates
  - Settings
  - API Keys

**13. Manage Users**
- User clicks "User Management" tab
- User sees table of all users:
  - Name
  - Email
  - Role (Regular User, Legal Reviewer, Admin)
  - Status (Active, Inactive)
  - Last login date
- User can:
  - Click **"Add User"** button
  - Fill in new user details (name, email, role)
  - Send invitation email
  - Edit existing user's role
  - Deactivate/activate users
  - Delete users

**14. Create/Edit Templates**
- User clicks "Templates" tab in Admin
- User sees all contract templates
- User clicks **"Create Template"** button
- User fills in:
  - Template name
  - Category (Legal, Employment, Vendor, Partnership)
  - Description
  - Upload base PDF
  - Define fillable fields (name, dates, amounts, etc.)
  - Set validation rules
- User clicks **"Save Template"**
- Template becomes available to all users

**15. Edit Existing Template**
- User clicks on template name
- User sees template details page
- User clicks **"Edit Template"** button
- User can:
  - Update template information
  - Modify fields
  - Upload new version
  - See usage statistics (how many times used)
  - Delete template (with confirmation)

**16. Configure Settings**
- User clicks "Settings" tab
- User can configure:
  - Email notifications (on/off)
  - Approval workflows (who needs to approve)
  - Validation rules (strictness level)
  - Document retention period
  - Default contract values

**17. Manage API Keys**
- User clicks "API Keys" tab
- User can:
  - Generate new API key
  - View existing keys
  - Revoke keys
  - Set key permissions

---

## 📊 Quick Comparison Table

| Feature | Regular User | Legal Reviewer | Admin |
|---------|:------------:|:--------------:|:-----:|
| Login to system | ✅ | ✅ | ✅ |
| View dashboard | ✅ | ✅ | ✅ |
| Generate contracts | ✅ | ✅ | ✅ |
| Upload proposals | ✅ | ✅ | ✅ |
| View contracts | ✅ | ✅ | ✅ |
| Validate contracts | ❌ | ✅ | ✅ |
| Approve/reject contracts | ❌ | ✅ | ✅ |
| Review proposals | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Create templates | ❌ | ❌ | ✅ |
| Edit settings | ❌ | ❌ | ✅ |
| Manage API keys | ❌ | ❌ | ✅ |

---

## 🗺️ Navigation Map

### Sidebar Menu (What Each User Sees)

**Regular User sees:**
- 🏠 Dashboard
- 📄 Contracts (list of all contracts)
- ➕ Generate Contract (create new)
- 🔍 Validate (view only - redirects to contract details)
- 📋 Proposals (upload and view)
- 📑 Templates (browse and use)

**Legal Reviewer sees (additional):**
- Same as Regular User
- ✅ Validate now works (can run validation)
- 👍 Can see Approve/Reject buttons on contracts

**Admin sees (additional):**
- Same as Legal Reviewer
- ⚙️ Admin (user management, templates, settings)

---

## 💡 Example User Stories

### Story 1: Regular User Creates a Contract

1. **Sarah** (Regular User) logs in
2. Sees her Dashboard with 5 contracts
3. Clicks **"Generate Contract"**
4. Selects "NDA Template"
5. Fills in: Company A, Company B, Start Date, Term length
6. Clicks **"Generate"**
7. Sees success message: "Contract created successfully!"
8. Contract appears in her list as "Draft" status
9. System sends notification to Legal Team for approval

### Story 2: Legal Reviewer Approves Contract

1. **Mike** (Legal Reviewer) logs in
2. Sees Dashboard shows "3 Pending Approvals"
3. Clicks on Pending Approvals card
4. Sees Sarah's NDA in the list
5. Clicks on the contract
6. Reviews contract PDF
7. Checks validation results (all green - low risk)
8. Clicks **"Approve"** button
9. Adds note: "Approved - standard NDA terms"
10. Contract status changes to "Active"
11. Sarah gets email: "Your contract has been approved!"

### Story 3: Admin Adds New User

1. **Jessica** (Admin) logs in
2. Clicks **"Admin"** in sidebar
3. Clicks **"User Management"** tab
4. Clicks **"Add User"** button
5. Fills in:
   - Name: John Smith
   - Email: john@company.com
   - Role: Legal Reviewer
6. Clicks **"Send Invitation"**
7. John receives email with login link
8. John appears in user table

---

## 🔄 Common Workflows

### Workflow A: Contract Creation to Approval

```
Regular User → Generate Contract → System Creates Draft
    ↓
Legal Reviewer → Receives Notification → Reviews Contract
    ↓
Legal Reviewer → Validates if Needed → Checks Risks
    ↓
Legal Reviewer → Approves OR Rejects
    ↓
If Approved → Contract Active → Both Parties Notified
If Rejected → Back to Draft → User Gets Feedback
```

### Workflow B: Proposal Submission

```
Regular User → Upload Proposal PDF → Fill Details
    ↓
System → Saves to Proposals List
    ↓
Legal Reviewer → Reviews Proposal → Sees Key Info
    ↓
Legal Reviewer → Accept OR Reject
    ↓
If Accepted → Create Contract from Proposal
If Rejected → User Notified with Reason
```

### Workflow C: Template Usage

```
User → Browse Templates → Click Template
    ↓
User → View Template Details → See Required Fields
    ↓
User → Click "Use Template"
    ↓
System → Opens Generate Page with Template Pre-loaded
    ↓
User → Fill Remaining Fields → Generate Contract
```

---

## 📝 Notes for Making Changes

### If you want to modify workflows:

**To add a new user action:**
- Identify which role should have this action
- Determine which page it appears on
- Decide what button/link text to use

**To change approval process:**
- Current: Legal Reviewer approves
- To change: Update who can see "Approve" button

**To add new contract status:**
- Current statuses: Draft, Pending Approval, Active, Expired
- New status needs: Color, label, what triggers it

**To modify dashboard cards:**
- Current: 4 cards show statistics
- Can add new cards or change calculations

**To change sidebar menu:**
- Update which roles see which menu items
- Rearrange menu order

---

## ❓ Questions to Ask When Planning Changes

1. **Which user role needs this feature?**
   - Just one role or multiple?
   
2. **Where should it appear in the app?**
   - New page or existing page?
   - In sidebar or as a button?

3. **What should happen when user clicks it?**
   - Open a form?
   - Show a popup?
   - Navigate to new page?

4. **Who needs to be notified?**
   - Other users?
   - Emails sent?

5. **What data needs to be saved?**
   - New information collected?
   - Existing data updated?

---

## ✅ This Document Helps You:

- ✅ Understand who uses the system and what they can do
- ✅ See step-by-step user journeys
- ✅ Identify where to make workflow changes
- ✅ Communicate requirements to developers
- ✅ Plan new features based on user roles

**Next Step:** Mark which workflows you want to change and describe the desired new flow!
