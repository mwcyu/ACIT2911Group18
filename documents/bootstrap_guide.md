## ✅ Bootstrap 5 Utility Cheat Sheet (Markdown)

### 📦 Spacing (Margin & Padding)

Format: `{property}{side}-{breakpoint?}-{size}`

| Prefix | Meaning      |
| ------ | ------------ |
| `m`    | Margin       |
| `p`    | Padding      |
| `t`    | Top          |
| `b`    | Bottom       |
| `s`    | Start (left) |
| `e`    | End (right)  |
| `x`    | Left & right |
| `y`    | Top & bottom |

**Examples:**

- `mt-3` → margin-top: `1rem`
- `px-2` → padding-left & right: `0.5rem`
- `mb-lg-4` → margin-bottom `1.5rem` on large screens and up

**Size scale:**

| Class    | Spacing (rem) |
| -------- | ------------- |
| `*-0`    | 0             |
| `*-1`    | 0.25rem       |
| `*-2`    | 0.5rem        |
| `*-3`    | 1rem          |
| `*-4`    | 1.5rem        |
| `*-5`    | 3rem          |
| `*-auto` | auto          |

---

### 💡 Display

| Class       | Description            |
| ----------- | ---------------------- |
| `d-block`   | Display block          |
| `d-inline`  | Display inline         |
| `d-flex`    | Display flex           |
| `d-none`    | Hidden (display: none) |
| `d-md-flex` | Flex display on `md+`  |

---

### 📱 Responsive Breakpoints

Used for responsive variations like `mt-md-3`, `d-lg-flex`

| Breakpoint | Min Width |
| ---------- | --------- |
| `sm`       | 576px     |
| `md`       | 768px     |
| `lg`       | 992px     |
| `xl`       | 1200px    |
| `xxl`      | 1400px    |

---

### 🎯 Flexbox Utilities

| Class                    | Description                 |
| ------------------------ | --------------------------- |
| `justify-content-start`  | Left align                  |
| `justify-content-center` | Center align                |
| `justify-content-end`    | Right align                 |
| `align-items-center`     | Vertical center             |
| `flex-column`            | Stack vertically            |
| `flex-md-row`            | Row layout on `md+` screens |
| `gap-2`, `gap-4`         | Spacing between items       |

---

### 🎨 Colors

| Class                | Example Use                    |
| -------------------- | ------------------------------ |
| `text-primary`       | Primary blue text              |
| `text-muted`         | Muted gray text                |
| `bg-light`           | Light background               |
| `bg-dark text-white` | Dark background, white text    |
| `text-bg-success`    | Badge background (e.g., green) |

---

### 🔢 Typography

| Class         | Description              |
| ------------- | ------------------------ |
| `fw-bold`     | Bold text                |
| `fw-light`    | Light text               |
| `text-center` | Centered text            |
| `text-start`  | Left-aligned text        |
| `fs-1`–`fs-6` | Font sizes (1 = largest) |

---

### 🧱 Grid System

| Class                 | Description                      |
| --------------------- | -------------------------------- |
| `container`           | Fixed-width wrapper              |
| `row`                 | Row inside container             |
| `col-6`, `col-md-4`   | Responsive column widths         |
| `g-3`, `gx-4`, `gy-2` | Gutter (spacing) between columns |

---

### 🔘 Buttons

| Class                       | Style                  |
| --------------------------- | ---------------------- |
| `btn btn-primary`           | Solid primary button   |
| `btn btn-outline-secondary` | Outlined button        |
| `btn-sm`, `btn-lg`          | Small or large buttons |
| `w-100`                     | Full-width button      |

---

### 📎 Components (Quick Class Reminders)

| Component | Common Classes                                  |
| --------- | ----------------------------------------------- |
| Navbar    | `navbar`, `navbar-expand`, `bg-*`, `sticky-top` |
| Cards     | `card`, `card-body`, `card-title`               |
| Alerts    | `alert alert-success` / `alert-danger`          |
| Badges    | `badge`, `text-bg-info`, `text-bg-warning`      |
| Form      | `form-control`, `form-label`, `form-check`      |
