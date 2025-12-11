import pandas as pd
import re
import hashlib


def is_empty_value(value):
    """Check if value is NaN or 'nan' string."""
    return pd.isna(value) or value == 'nan'


def clean_string_column(series):
    """Clean string columns: trim whitespace and remove multiple spaces."""
    return series.astype(str).apply(
        lambda x: re.sub(r' +', ' ', str.strip(x)) if not is_empty_value(x) else ''
    )


def convert_to_lowercase(series):
    """Convert all string values to lowercase."""
    return series.apply(
        lambda x: x.lower() if not is_empty_value(x) and isinstance(x, str) else ''
    )


def remove_text_in_parentheses(text):
    """Remove all text inside parentheses and the parentheses themselves."""
    if is_empty_value(text):
        return ''
    
    text = str(text)
    # Remove text inside parentheses - apply multiple times to handle nested parentheses
    for _ in range(10):
        new_text = re.sub(r'\([^()]*\)', '', text)
        if new_text == text:  # No more changes
            break
        text = new_text
    
    return re.sub(r'\s+', ' ', text).strip()


def remove_company_suffixes(text):
    """Remove common company suffixes from organization names."""
    if is_empty_value(text):
        return ''
    
    text = str(text).strip().lower()
    
    # Define company suffixes to remove (sorted by length, longest first)
    suffixes = [
        # Combined patterns with ltd (with spaces)
        ' (pty) ltd.', ' (pty) ltd', '(pty) ltd.', '(pty) ltd',
        ' pty (ltd).', ' pty (ltd)', 'pty (ltd).', 'pty (ltd)',
        ' pty ltd.', ' pty ltd', 'pty ltd.', 'pty ltd',
        # Combined patterns with ltd (no spaces between)
        ' (pty)ltd.', ' (pty)ltd', '(pty)ltd.', '(pty)ltd',
        ' pty(ltd).', ' pty(ltd)', 'pty(ltd).', 'pty(ltd)',
        ' ptyltd.', ' ptyltd', 'ptyltd.', 'ptyltd',
        # Combined patterns with ldt (typo variant, with spaces)
        ' (pty) ldt.', ' (pty) ldt', '(pty) ldt.', '(pty) ldt',
        ' pty (ldt).', ' pty (ldt)', 'pty (ldt).', 'pty (ldt)',
        ' pty ldt.', ' pty ldt', 'pty ldt.', 'pty ldt',
        # Combined patterns with ldt (no spaces between)
        ' (pty)ldt.', ' (pty)ldt', '(pty)ldt.', '(pty)ldt',
        ' pty(ldt).', ' pty(ldt)', 'pty(ldt).', 'pty(ldt)',
        ' ptyldt.', ' ptyldt', 'ptyldt.', 'ptyldt',
        # Individual suffixes with parentheses
        ' (ltd).', ' (ltd)', '(ltd).', '(ltd)',
        ' (ldt).', ' (ldt)', '(ldt).', '(ldt)',
        ' (pty).', ' (pty)', '(pty).', '(pty)',
        ' (co).', ' (co)', '(co).', '(co)',
        ' (inc).', ' (inc)', '(inc).', '(inc)',
        ' (llc).', ' (llc)', '(llc).', '(llc)',
        ' (corp).', ' (corp)', '(corp).', '(corp)',
        # Individual suffixes without parentheses
        ' ltd.', ' ltd', ' ldt.', ' ldt',
        ' pty.', ' pty',
        ' co.', ' co', ' inc.', ' inc',
        ' llc.', ' llc', ' corp.', ' corp',
        ' corporation.', ' corporation',
        ' limited.', ' limited',
        ' incorporated.', ' incorporated',
        ' company.', ' company',
    ]
    
    suffixes.sort(key=len, reverse=True)
    
    # Remove suffixes - keep looping until no more changes
    for _ in range(10):
        changed = False
        for suffix in suffixes:
            if text.endswith(suffix):
                text = text[:-len(suffix)].strip()
                changed = True
                break
        if not changed:
            break
    
    # Regex backup for edge cases
    regex_patterns = [
        r'\s*\(?\s*pty\s*\)?\s*\(?\s*(ltd|ldt)\s*\)?\s*\.?\s*$',
        r'\s*\(?\s*pty\s*\)?\s*(ltd|ldt)\s*\.?\s*$',
        r'\s*pty\s*\(?\s*(ltd|ldt)\s*\)?\s*\.?\s*$',
        r'\s*ptyltd\s*\.?\s*$',
        r'\s*ptyldt\s*\.?\s*$',
        r'\s+\(?\s*pty\s*\)?\s*\.?\s*$',
        r'\s*\(?\s*pty\s*\)?\s*$',
        r'\s+pty\s*\.?\s*$',
        r'\s*pty\s*\.?\s*$',
        r'\s+\(?\s*(ltd|ldt|limited|co|inc|llc|corp|corporation|incorporated|company)\s*\)?\s*\.?\s*$',
    ]
    
    # Apply regex patterns
    for _ in range(5):
        for pattern in regex_patterns:
            new_text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            if new_text != text:
                text = new_text
                break
    
    return re.sub(r'\s+', ' ', text).strip(' .,;:')


def remove_street_types(text):
    """Remove street type suffixes (Street, Avenue, Road, and variations) from addresses."""
    if is_empty_value(text):
        return ''
    
    text = str(text).strip().lower()
    
    # Use regex to remove street types anywhere in the text
    regex_patterns = [
        r'\s+(street|st\.?|avenue|ave\.?|road|rd\.?)(?=\s|,|$)',
        r'\b(street|st\.?|avenue|ave\.?|road|rd\.?)(?=\s|,|$)',
    ]
    
    for _ in range(5):
        for pattern in regex_patterns:
            new_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            if new_text != text:
                text = new_text
                break
    
    # Direct string replacement for common patterns
    street_types = [
        ' street,', ' street.', ' street ',
        ' st,', ' st.', ' st ',
        ' avenue,', ' avenue.', ' avenue ',
        ' ave,', ' ave.', ' ave ',
        ' road,', ' road.', ' road ',
        ' rd,', ' rd.', ' rd ',
    ]
    
    street_types.sort(key=len, reverse=True)
    
    for _ in range(10):
        changed = False
        for street_type in street_types:
            if street_type in text:
                text = text.replace(street_type, ' ')
                changed = True
                break
        if not changed:
            break
    
    # Final cleanup - remove commas and periods, then clean up extra spaces
    text = text.replace(',', ' ').replace('.', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def clean_phone_number(series):
    """Remove non-numerical characters from phone numbers."""
    return series.astype(str).apply(
        lambda x: re.sub(r'[^0-9]', '', x) if not is_empty_value(x) else ''
    )


def extract_last_nine_digits(series):
    """Extract the last nine characters from phone numbers."""
    return series.astype(str).apply(
        lambda x: x[-9:] if not is_empty_value(x) and len(x) >= 9 else ('' if is_empty_value(x) else x)
    )


def get_first_five_characters(text):
    """Extract the first five characters (including spaces) from text."""
    if is_empty_value(text):
        return ''
    text = str(text)
    return text[:5] if len(text) >= 5 else text


def get_last_five_characters(text):
    """Extract the last five characters from text."""
    if is_empty_value(text):
        return ''
    text = str(text)
    return text[-5:] if len(text) >= 5 else text


def get_output_filename():
    """Return the output filename."""
    return 'output-hashed.csv'


def hash_column(series):
    """Hash a column using SHA256."""
    return series.astype(str).apply(
        lambda x: hashlib.sha256(x.encode()).hexdigest() if x else ''
    )


def main():
    """Main processing function."""
    # Read input CSV
    data = pd.read_csv('input.csv')
    
    # General data cleaning: trim, remove multiple spaces, and convert to lowercase
    for column in data.columns:
        if data[column].dtype == 'object':
            data[column] = clean_string_column(data[column])
            data[column] = convert_to_lowercase(data[column])
    
    # Process Org Name
    if 'Org Name' in data.columns:
        data['Org Name'] = data['Org Name'].apply(remove_text_in_parentheses)
        data['Org Name'] = data['Org Name'].apply(remove_company_suffixes)
        data['Org Name'] = data['Org Name'].apply(remove_company_suffixes)  # Run twice
        
        # Add derived columns
        data['Org Name First 5 Letters'] = data['Org Name'].apply(get_first_five_characters)
        data['Org Name Last 5 Characters'] = data['Org Name'].apply(get_last_five_characters)
    
    # Process Org Address
    if 'Org Address' in data.columns:
        data['Org Address'] = data['Org Address'].apply(remove_street_types)
    
    # Process Phone Number
    if 'Phone Number' in data.columns:
        data['Phone Number'] = clean_phone_number(data['Phone Number'])
        data['Phone Number'] = extract_last_nine_digits(data['Phone Number'])
    
    # Replace NaN values and 'nan' strings with empty strings
    data = data.fillna('')
    for column in data.columns:
        if data[column].dtype == 'object':
            data[column] = data[column].replace('nan', '', regex=False)
    
    # Hash specified columns
    columns_to_hash = [
        'Org Name',
        'Org Address',
        'Phone Number',
        'Company Email',
        'Company Website',
        'Org Name First 5 Letters',
        'Org Name Last 5 Characters',
    ]
    
    for column in columns_to_hash:
        if column in data.columns:
            data[column] = hash_column(data[column])
    
    # Save output
    output_filename = get_output_filename()
    data.to_csv(output_filename, index=False)
    print(f"Data processing complete! Output saved to {output_filename}")


if __name__ == '__main__':
    main()
