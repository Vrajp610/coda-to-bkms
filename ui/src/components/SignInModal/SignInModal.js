import { useState, useEffect } from 'react';
import { CONSTANTS } from '../../utils/CONSTANTS';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '../Button/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

/** * SignInModal component for user authentication.
 * Displays a modal dialog for signing in with email and password.
 * @param {Object} props - Component properties.
 * @param {boolean} props.open - Whether the modal is open.
 * @param {Function} props.onClose - Function to call when the modal is closed.
 * @param {Function} props.onSuccess - Function to call on successful sign-in.
 */
const SignInModal = ({ open, onClose, onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open) {
      setEmail('');
      setPassword('');
      setError('');
    }
  }, [open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }
    if (email !== CONSTANTS.VALID_EMAIL || password !== CONSTANTS.VALID_PASSWORD) {
      setError('Invalid email or password.');
      return;
    }
    setError('');
    setEmail('');
    setPassword('');
    onSuccess();
    onClose();
  };

  const handleClose = () => {
    setError('');
    setEmail('');
    setPassword('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>Sign In</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            fullWidth
            margin="normal"
            required
          />
          {error && (
            <Typography color="error" variant="body2" sx={{ mt: 1 }}>
              {error}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} variant="outlined">Cancel</Button>
          <Button type="submit" variant="contained">Sign In</Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default SignInModal;