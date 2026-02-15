import React from 'react';

const TransactionItem = ({ transaction, onDelete, onEdit }) => {
    return (
        <tr style={{ borderBottom: '1px solid #ddd' }}>
            <td style={tdStyle}>{transaction.date}</td>
            <td style={tdStyle}>{transaction.title}</td>
            <td style={tdStyle}>{transaction.category}</td>
            <td style={tdStyle}>${transaction.amount.toFixed(2)}</td>
            <td style={tdStyle}>
                <div style={{ display: 'flex', gap: '10px' }}>
                    {/* Update/Edit Button */}
                    <button 
                        onClick={() => onEdit(transaction)} 
                        style={{ color: '#3498db', border: 'none', background: 'none', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                        Edit
                    </button>

                    {/* Delete Button */}
                    <button 
                        onClick={() => onDelete(transaction.id)} 
                        style={{ color: '#e74c3c', border: 'none', background: 'none', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                        Delete
                    </button>
                </div>
            </td>
        </tr>
    );
};

const tdStyle = { padding: '12px', textAlign: 'left' };

export default TransactionItem;