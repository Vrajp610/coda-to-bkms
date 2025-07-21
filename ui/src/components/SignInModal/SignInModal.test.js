import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SignInModal from './SignInModal';

describe('SignInModal', () => {
  const VALID_EMAIL = 'vrajptl0610@gmail.com';
  const VALID_PASSWORD = 'vraj';
  let onClose, onSuccess;

  beforeEach(() => {
    onClose = jest.fn();
    onSuccess = jest.fn();
  });

  it('renders when open', () => {
    render(<SignInModal open={true} onClose={onClose} onSuccess={onSuccess} />);
    expect(screen.getByRole('heading', { name: /Sign In/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/^Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password/i)).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<SignInModal open={false} onClose={onClose} onSuccess={onSuccess} />);
    expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
  });

  it('shows error if fields are empty', () => {
    render(<SignInModal open={true} onClose={onClose} onSuccess={onSuccess} />);
    const signInButton = screen.getAllByText('Sign In').find(
      (el) => el.tagName === 'BUTTON'
    );
    fireEvent.click(signInButton);
    expect(screen.getByText('Please enter both email and password.')).toBeInTheDocument();
  });

  it('shows error for invalid credentials', () => {
    render(<SignInModal open={true} onClose={onClose} onSuccess={onSuccess} />);
    fireEvent.change(screen.getByLabelText(/^Email/i), { target: { value: 'wrong@email.com' } });
    fireEvent.change(screen.getByLabelText(/^Password/i), { target: { value: 'wrongpass' } });
    const signInButton = screen.getAllByText('Sign In').find(
      (el) => el.tagName === 'BUTTON'
    );
    fireEvent.click(signInButton);
    expect(screen.getByText('Invalid email or password.')).toBeInTheDocument();
  });

  it('calls onSuccess and onClose on valid credentials', () => {
    render(<SignInModal open={true} onClose={onClose} onSuccess={onSuccess} />);
    fireEvent.change(screen.getByLabelText(/^Email/i), { target: { value: VALID_EMAIL } });
    fireEvent.change(screen.getByLabelText(/^Password/i), { target: { value: VALID_PASSWORD } });
    const signInButton = screen.getAllByText('Sign In').find(
      (el) => el.tagName === 'BUTTON'
    );
    fireEvent.click(signInButton);
    expect(onSuccess).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
    expect(screen.queryByText('Invalid email or password.')).not.toBeInTheDocument();
    expect(screen.queryByText('Please enter both email and password.')).not.toBeInTheDocument();
  });

  it('clears fields and error on close', () => {
    render(<SignInModal open={true} onClose={onClose} onSuccess={onSuccess} />);
    fireEvent.change(screen.getByLabelText(/^Email/i), { target: { value: 'test@email.com' } });
    fireEvent.change(screen.getByLabelText(/^Password/i), { target: { value: 'testpass' } });
    const signInButton = screen.getAllByText('Sign In').find(
      (el) => el.tagName === 'BUTTON'
    );
    fireEvent.click(signInButton);
    expect(screen.getByText('Invalid email or password.')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Cancel'));
    expect(onClose).toHaveBeenCalled();
  });

  it('clears error when modal is closed and reopened', async () => {
    const { rerender } = render(<SignInModal open={true} onClose={onClose} onSuccess={onSuccess} />);
    const signInButton = screen.getAllByText('Sign In').find(
      (el) => el.tagName === 'BUTTON'
    );
    fireEvent.click(signInButton);
    expect(screen.getByText('Please enter both email and password.')).toBeInTheDocument();
    rerender(<SignInModal open={false} onClose={onClose} onSuccess={onSuccess} />);
    rerender(<SignInModal open={true} onClose={onClose} onSuccess={onSuccess} />);
    await waitFor(() =>
      expect(screen.queryByText('Please enter both email and password.')).not.toBeInTheDocument()
    );
  });

  it('should clear error, email, and password and call onSuccess and onClose on valid submit', () => {
    render(<SignInModal open={true} onClose={onClose} onSuccess={onSuccess} />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'vrajptl0610@gmail.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'vraj' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    expect(onSuccess).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });
});