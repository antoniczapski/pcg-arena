import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import '../styles/builder.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [status, setStatus] = useState<'form' | 'submitting' | 'success' | 'error'>('form');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }
    
    if (newPassword.length < 8) {
      setMessage('Password must be at least 8 characters');
      return;
    }
    
    if (!token) {
      setStatus('error');
      setMessage('Invalid reset link. No token provided.');
      return;
    }
    
    setStatus('submitting');
    setMessage('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/v1/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: newPassword }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setStatus('success');
        setMessage(data.message || 'Password updated successfully!');
        
        // Redirect to login after a delay
        setTimeout(() => {
          navigate('/builder');
        }, 3000);
      } else {
        setStatus('error');
        setMessage(data.error?.message || 'Failed to reset password.');
      }
    } catch (error) {
      console.error('Reset password error:', error);
      setStatus('error');
      setMessage('An error occurred. Please try again.');
    }
  };

  if (!token) {
    return (
      <div className="verify-email-page">
        <div className="verify-email-card">
          <div className="verify-icon error">❌</div>
          <h2>Invalid Reset Link</h2>
          <p>This password reset link is invalid or has expired.</p>
          <button 
            className="login-button"
            onClick={() => navigate('/builder')}
          >
            Go to Sign In
          </button>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="verify-email-page">
        <div className="verify-email-card">
          <div className="verify-icon success">✅</div>
          <h2>Password Updated!</h2>
          <p>{message}</p>
          <p>Redirecting to sign in...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="verify-email-page">
      <div className="verify-email-card">
        <h2>Reset Password</h2>
        <p>Enter your new password below.</p>
        
        {status === 'error' && message && (
          <div className="auth-error">{message}</div>
        )}
        
        <form onSubmit={handleSubmit} className="auth-form" style={{ marginTop: '1rem' }}>
          <div className="form-group">
            <label htmlFor="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="At least 8 characters"
              required
              disabled={status === 'submitting'}
              minLength={8}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter your password"
              required
              disabled={status === 'submitting'}
            />
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={status === 'submitting'}
          >
            {status === 'submitting' ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </div>
    </div>
  );
}

