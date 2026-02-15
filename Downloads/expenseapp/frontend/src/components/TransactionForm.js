import React, { useState, useEffect } from 'react';
import API from '../services/api';

const TransactionForm = ({ onTransactionAdded, editingTransaction, onCancelEdit }) => {
    const [formData, setFormData] = useState({
        title: '', amount: '', category: 'Food', date: new Date().toISOString().split('T')[0]
    });

    // 1. Detect if we are in "Edit Mode"
    useEffect(() => {
        if (editingTransaction) {
            setFormData({
                title: editingTransaction.title,
                amount: editingTransaction.amount,
                category: editingTransaction.category,
                date: editingTransaction.date
            });
        } else {
            // Reset form if not editing
            setFormData({ title: '', amount: '', category: 'Food', date: new Date().toISOString().split('T')[0] });
        }
    }, [editingTransaction]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingTransaction) {
                // UPDATE existing record (PUT)
                await API.put(`/transactions/${editingTransaction.id}`, formData);
                onCancelEdit(); // Exit edit mode
            } else {
                // ADD new record (POST)
                await API.post('/transactions', formData);
            }
            
            // Common cleanup
            setFormData({ title: '', amount: '', category: 'Food', date: new Date().toISOString().split('T')[0] });
            onTransactionAdded(); // Refresh the list
        } catch (err) {
            alert("Error saving transaction");
            console.error(err);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={formContainerStyle}>
            <h3 style={{ width: '100%', marginBottom: '15px' }}>
                {editingTransaction ? "📝 Edit Transaction" : "➕ Add New Transaction"}
            </h3>
            
            <input type="text" placeholder="Title" value={formData.title} required 
                style={inputStyle} onChange={e => setFormData({...formData, title: e.target.value})} />
            
            <input type="number" placeholder="Amount" value={formData.amount} required 
                style={inputStyle} onChange={e => setFormData({...formData, amount: e.target.value})} />
            
            <select value={formData.category} style={inputStyle} 
                onChange={e => setFormData({...formData, category: e.target.value})}>
                <option value="Food">Food</option>
                <option value="Rent">Rent</option>
                <option value="Transport">Transport</option>
                <option value="Entertainment">Entertainment</option>
                <option value="Shopping">Shopping</option>
            </select>
            
            <input type="date" value={formData.date} style={inputStyle} 
                onChange={e => setFormData({...formData, date: e.target.value})} />

            <div style={{ display: 'flex', gap: '10px', width: '100%' }}>
                <button type="submit" style={editingTransaction ? updateBtnStyle : addBtnStyle}>
                    {editingTransaction ? "Save Changes" : "Add Transaction"}
                </button>
                
                {editingTransaction && (
                    <button type="button" onClick={onCancelEdit} style={cancelBtnStyle}>
                        Cancel
                    </button>
                )}
            </div>
        </form>
    );
};

// --- Modern Inline Styles ---
const formContainerStyle = { display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '30px', background: '#fcfcfc', padding: '20px', borderRadius: '10px', border: '1px solid #eee' };
const inputStyle = { flex: '1', minWidth: '150px', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' };
const addBtnStyle = { background: '#2ecc71', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' };
const updateBtnStyle = { background: '#3498db', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' };
const cancelBtnStyle = { background: '#95a5a6', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer' };

export default TransactionForm;