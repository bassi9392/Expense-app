import React, { useState, useEffect, useCallback } from 'react';
import API from '../services/api';
import TransactionForm from '../components/TransactionForm';
import TransactionItem from '../components/TransactionItem';

const Explorer = () => {
    const [transactions, setTransactions] = useState([]);
    const [search, setSearch] = useState('');
    // NEW: State to hold the transaction currently being edited
    const [editingTransaction, setEditingTransaction] = useState(null);

    const fetchTransactions = useCallback(async () => {
        try {
            const res = await API.get(`/transactions?search=${search}`);
            setTransactions(res.data.data);
        } catch (err) { 
            console.error("Error fetching transactions:", err); 
        }
    }, [search]);

    useEffect(() => {
        fetchTransactions();
    }, [fetchTransactions]);

    const handleDelete = async (id) => {
        if (window.confirm("Are you sure you want to delete this?")) {
            await API.delete(`/transactions/${id}`);
            fetchTransactions();
        }
    };

    // NEW: Function to handle when the 'Edit' button is clicked in the Item
    const handleEditClick = (transaction) => {
        setEditingTransaction(transaction);
        // Scroll to top so user sees the form is now in "Edit Mode"
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // NEW: Function to clear the edit mode after saving or canceling
    const clearEdit = () => {
        setEditingTransaction(null);
    };

    return (
        <div>
            <h2>Transaction Explorer</h2>
            
            <input 
                type="text" 
                placeholder="Search transactions..." 
                style={searchStyle}
                onChange={(e) => setSearch(e.target.value)} 
            />
            
            {/* UPDATED: Pass editingTransaction and clearEdit to the form */}
            <TransactionForm 
                onTransactionAdded={fetchTransactions} 
                editingTransaction={editingTransaction}
                onCancelEdit={clearEdit}
            />

            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                <thead style={{ background: '#f8f9fa' }}>
                    <tr>
                        <th style={thStyle}>Date</th>
                        <th style={thStyle}>Title</th>
                        <th style={thStyle}>Category</th>
                        <th style={thStyle}>Amount</th>
                        <th style={thStyle}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {transactions.map(t => (
                        <TransactionItem 
                            key={t.id} 
                            transaction={t} 
                            onDelete={handleDelete}
                            onEdit={handleEditClick} // NEW: Passing the edit handler
                        />
                    ))}
                </tbody>
            </table>
        </div>
    );
};

const searchStyle = { width: '100%', padding: '12px', marginBottom: '20px', borderRadius: '5px', border: '1px solid #ccc' };
const thStyle = { padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' };

export default Explorer;