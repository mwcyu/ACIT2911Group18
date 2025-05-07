# Bootstrap Classes Documentation

## Navigation Classes

### Core Navigation Elements

- `navbar`: Creates a navigation bar container
- `navbar-expand-lg`: Expands navbar horizontally on large screens (992px+), collapses on smaller screens
- `bg-body-tertiary`: Applies a subtle background color to the navbar
- `container`: Creates a centered, responsive wrapper with padding

### Brand and Toggle Elements

- `navbar-brand`: Styles the website logo/name with larger font size and padding
- `navbar-toggler`: Styles the mobile menu toggle button
- `navbar-toggler-icon`: Creates the hamburger menu icon

### Navigation Content

- `collapse`: Manages collapsible behavior
- `navbar-collapse`: Specific styling for collapsible navbar content
- `navbar-nav`: Styles the navigation list within navbar
- `me-auto`: Adds auto margin to right side
- `mb-2`: Adds margin-bottom (0.5rem)
- `mb-lg-0`: Removes bottom margin on large screens

### Navigation Items

- `nav-item`: Styles individual navigation items
- `nav-link`: Styles navigation links with padding and hover states
- `active`: Highlights current/active navigation item

## Container and Spacing Classes

- `container`: Creates a responsive fixed-width container
- `mt-3`: Adds margin-top (1rem)
- `mt-5`: Adds margin-top (3rem)
- `mb-3`: Adds margin-bottom (1rem)
- `py-3`: Adds padding on top and bottom (1rem)
- `gap-2`: Adds gap spacing between flex/grid items (0.5rem)

## Utility Classes

- `d-flex`: Creates a flexbox container
- `text-end`: Aligns text to the right
- `text-muted`: Makes text a lighter gray color
- `text-success`: Colors text with the success theme color (usually green)
- `small`: Reduces text size
- `border-top`: Adds a border to the top of an element

## Button Classes

- `btn`: Base button class
- `btn-sm`: Makes a small-sized button
- `btn-primary`: Primary colored button (usually blue)
- `btn-outline-primary`: Outlined version of primary button
- `btn-outline-danger`: Outlined version of danger button (usually red)

## Dropdown Classes

- `dropdown`: Container for dropdown elements
- `dropdown-toggle`: Adds dropdown toggle styling and arrow
- `dropdown-menu`: Styles the dropdown container
- `dropdown-item`: Styles individual dropdown items

## Responsive Classes

- `mt-lg-0`: Removes margin-top on large screens
- `navbar-expand-lg`: Expands navbar on large screens

## Form and Input Classes

- `form-control`: Basic form input styling
- `form-label`: Styles form labels
- `form-text`: Helper text below form inputs
- `form-check`: Container for checkboxes and radios
- `form-select`: Styled select dropdowns

## Additional Navigation Elements

- `nav-link`: Styles navigation links
- `navbar-nav`: Container for navigation items
- `navbar-brand`: Website/brand logo styling

## State and Interactive Classes

- `active`: Shows current/active state
- `disabled`: Shows disabled state
- `collapsed`: For collapsible elements
- `show`: Shows collapsed/hidden elements

## Usage Notes

These classes work together to create a responsive navigation bar that:

- Collapses into a mobile menu on small screens
- Expands horizontally on larger screens
- Has proper spacing and alignment
- Includes a hamburger menu for mobile views
- Shows active page status

And can be combined to create:

- Responsive layouts with proper spacing
- Interactive navigation elements
- Properly styled forms and buttons
- Clear visual hierarchy
- Consistent mobile-friendly interfaces

Remember:

- Classes can be combined for multiple effects
- Responsive classes use breakpoints (sm, md, lg, xl, xxl)
- Utility classes provide quick styling without custom CSS
- Bootstrap's grid system uses these classes for layout control
