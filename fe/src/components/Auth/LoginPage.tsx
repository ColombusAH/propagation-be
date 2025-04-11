import { useState } from 'react';
import { TextInput, PasswordInput, Paper, Title, Container, Button, Text, Stack } from '@mantine/core';
import { useAuth } from '../../contexts/AuthContext';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, error, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
    // If login is successful, the user will be set in the AuthContext
    // and the protected routes will handle the redirection
  };

  return (
    <Container size={420} my={40}>
      <Title ta="center">Welcome back!</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Enter your credentials to continue
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={handleSubmit}>
          <Stack>
            <TextInput
              label="Email"
              placeholder="Your email"
              value={email}
              onChange={(e) => setEmail(e.currentTarget.value)}
              required
            />

            <PasswordInput
              label="Password"
              placeholder="Your password"
              value={password}
              onChange={(e) => setPassword(e.currentTarget.value)}
              required
            />
          </Stack>

          {error && (
            <Text color="red" size="sm" mt="md">
              {error}
            </Text>
          )}

          <Button fullWidth mt="xl" type="submit" loading={isLoading}>
            Sign in
          </Button>
        </form>
      </Paper>
    </Container>
  );
}; 