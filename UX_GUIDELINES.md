# UX Guidelines - HealthGYM System
**Owned by: Yeldana Kadenova**

## Phase 4: Usability Polish - Simplicity Metric

### Key Principle: Maximum 2 Clicks for Key Flows

All critical user journeys must be completable in **maximum 2 clicks** from any starting point.

### Key Flows Verified:

1. **Home → Register/Login → Dashboard**
   - Click 1: Home page → "Join Now" or "Member Login" button
   - Click 2: Submit registration/login form → Auto-redirect to Dashboard
   - ✅ **Status: 2 clicks**

2. **Dashboard → Leaderboard**
   - Click 1: Dashboard sidebar → "Leaderboard" link
   - ✅ **Status: 1 click** (within limit)

3. **Dashboard → Tournaments**
   - Click 1: Dashboard sidebar → "Tournaments" link
   - ✅ **Status: 1 click** (within limit)

4. **Dashboard → Quick Actions**
   - Quick action buttons on dashboard provide 1-click access to:
     - View Leaderboard
     - Join Tournament
     - Submit Challenge Score
   - ✅ **Status: 1 click** (within limit)

5. **Home → Leaderboard (Guest Access)**
   - Click 1: Home page → "View Leaderboard" button
   - ✅ **Status: 1 click** (within limit)

### UI Alignment Standards

All pages follow consistent alignment using:
- **Design System CSS** (`design-system.css`) with standardized spacing variables
- **Bootstrap 5** grid system for responsive layouts
- **Consistent padding/margins** using CSS variables:
  - `--spacing-xs`: 0.25rem (4px)
  - `--spacing-sm`: 0.5rem (8px)
  - `--spacing-md`: 1rem (16px)
  - `--spacing-lg`: 1.5rem (24px)
  - `--spacing-xl`: 2rem (32px)

### Responsive Design

- **Mobile-first approach**: All layouts adapt to mobile screens
- **Breakpoint**: 768px for tablet/mobile transitions
- **Sidebar**: Collapses on mobile, becomes hamburger menu
- **Cards**: Stack vertically on mobile, grid layout on desktop

### Performance Targets

- **Main Content Paint (MCP)**: < 1 second ✅
- **Leaderboard API Latency**: < 2 seconds ✅
- **Lazy Loading**: Implemented for images and non-critical resources ✅

### Navigation Structure

```
Home (index.html)
├── Login (login.html) → Dashboard (dashboard.html)
├── Register (register.html) → Dashboard (dashboard.html)
└── Leaderboard (leaderboard.html) [Guest Access]

Dashboard (dashboard.html)
├── Overview (current page)
├── Tournaments (tournaments.html)
└── Leaderboard (leaderboard.html)
```

### Accessibility

- Semantic HTML5 elements
- ARIA labels where appropriate
- Keyboard navigation support
- High contrast color scheme
- Responsive text sizing

### Design System Colors

- **Primary**: #198754 (Green)
- **Secondary**: #6c757d (Gray)
- **Success**: #198754
- **Warning**: #ffc107
- **Danger**: #dc3545
- **Dark**: #212529

### Typography

- **Primary Font**: System font stack (San Francisco, Segoe UI, Roboto)
- **Heading Font**: Inter (with fallback)
- **Base Size**: 16px (1rem)
- **Line Height**: 1.6

---

**Last Updated**: Phase 4 Completion
**Maintainer**: Yeldana Kadenova
