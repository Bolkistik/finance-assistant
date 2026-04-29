import React from 'react';

function DatePicker({ value, onChange }) {
    return (
        <input
            type="date"
            value={value}
            onChange={e => onChange(e.target.value)}
            style={{ padding: 8, fontSize: 16, margin: '10px 0'}}
        />
    );
}

export default DatePicker;