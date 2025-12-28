import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/builder.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [message, setMessage] = useState('Verifying your email...');

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('error');
      setMessage('Invalid verification link. No token provided.');
      return;
    }

    verifyEmail(token);
  }, [searchParams]);

  const verifyEmail = async (token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/auth/verify-email?token=${encodeURIComponent(token)}`, {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        setStatus('success');
        setMessage('Email verified successfully! Redirecting to your profile...');
        
        // Refresh user data to update is_email_verified
        await refreshUser();
        
        // Redirect to builder profile after a short delay
        setTimeout(() => {
          navigate('/builder');
        }, 2000);
      } else {
        const error = await response.json();
        setStatus('error');
        setMessage(error.error?.message || 'Verification failed. The link may have expired.');
      }
    } catch (error) {
      console.error('Verification error:', error);
      setStatus('error');
      setMessage('An error occurred during verification. Please try again.');
    }
  };

  return (
    <div className="verify-email-page">
      <div className="verify-email-card">
        {status === 'verifying' && (
          <>
            <div className="verify-icon loading">⏳</div>
            <h2>Verifying Email</h2>
            <p>{message}</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="verify-icon success">✅</div>
            <h2>Email Verified!</h2>
            <p>{message}</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="verify-icon error">❌</div>
            <h2>Verification Failed</h2>
            <p>{message}</p>
            <button 
              className="login-button"
              onClick={() => navigate('/builder')}
            >
              Go to Builder Profile
            </button>
          </>
        )}
      </div>
    </div>
  );
}

