import { Paper, Title, Container, Text, Stack, Loader } from '@mantine/core';
import { useAuth } from '../../contexts/AuthContext';
import { GoogleLogin } from '@react-oauth/google';
import type { CredentialResponse } from '@react-oauth/google';

export const LoginPage = () => {
  const { loginWithGoogle, error, isLoading } = useAuth();

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    console.log('Google Login Success:', credentialResponse);
    if (credentialResponse.credential) {
      await loginWithGoogle(credentialResponse.credential);
    } else {
      console.error("Google login failed: No credential received");
    }
  };

  const handleGoogleError = () => {
    console.log('Google Login Failed');
  };

  return (
    <Container size={420} my={40}>
      <Title ta="center">Welcome!</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Sign in with your Google account to continue
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <Stack align="center">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
          />

          {error && (
            <Text color="red" size="sm" mt="md">
              {error}
            </Text>
          )}

          {isLoading && <Loader mt="md" />}
        </Stack>
      </Paper>
    </Container>
  );
}; 