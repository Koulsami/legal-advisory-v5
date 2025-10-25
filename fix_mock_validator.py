"""Fix MockValidator to use correct ValidationError structure"""

# Read the file
with open('backend/emulators/mock_validator.py', 'r') as f:
    content = f.read()

# The ValidationError likely has these fields:
# field_name, message, severity, current_value

# Let's fix the ValidationError constructor calls properly
# We need to keep only ONE current_value parameter

import re

# Pattern to find ValidationError calls with duplicate current_value
# This is a more careful fix

fixed_content = content

# Fix pattern 1: Remove duplicate current_value lines
lines = content.split('\n')
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # If this line has ValidationError and next few lines might have duplicate current_value
    if 'ValidationError(' in line:
        # Collect the full constructor call
        constructor_lines = [line]
        j = i + 1
        paren_count = line.count('(') - line.count(')')
        
        while j < len(lines) and paren_count > 0:
            constructor_lines.append(lines[j])
            paren_count += lines[j].count('(') - lines[j].count(')')
            j += 1
        
        # Now fix this constructor call
        constructor_text = '\n'.join(constructor_lines)
        
        # Count current_value occurrences
        current_value_count = constructor_text.count('current_value=')
        
        if current_value_count > 1:
            # Remove all but the last current_value
            parts = constructor_text.split('current_value=')
            # Keep first part and last current_value assignment
            fixed_constructor = parts[0]
            # Add back only the LAST current_value
            if len(parts) > 1:
                # Take the last occurrence
                last_part = parts[-1]
                fixed_constructor += 'current_value=' + last_part
            
            fixed_lines.append(fixed_constructor)
        else:
            fixed_lines.extend(constructor_lines)
        
        i = j
    else:
        fixed_lines.append(line)
        i += 1

fixed_content = '\n'.join(fixed_lines)

# Write back
with open('backend/emulators/mock_validator.py', 'w') as f:
    f.write(fixed_content)

print("✅ Fixed mock_validator.py")
