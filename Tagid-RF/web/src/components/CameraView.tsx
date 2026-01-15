import { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import { BarcodeScanner } from '@/lib/barcode/BarcodeScanner';
import { theme } from '@/styles/theme';

interface CameraViewProps {
  onScan: (barcode: string) => void;
  onError?: (error: Error) => void;
}

const Container = styled.div`
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  background-color: ${theme.colors.gray[800]};
  border-radius: ${theme.borderRadius.lg};
  overflow: hidden;
  aspect-ratio: 4 / 3;
`;

const Video = styled.video`
  width: 100%;
  height: 100%;
  object-fit: cover;
  background-color: ${theme.colors.gray[800]};
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  gap: ${theme.spacing.md};
`;

const LoadingText = styled.p`
  font-size: ${theme.typography.fontSize.base};
  margin: 0;
`;

const Overlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
`;

const ScanLine = styled.div`
  width: 80%;
  height: 60%;
  border: 3px solid ${theme.colors.success};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.3);
  animation: pulse 2s ease-in-out infinite;

  @keyframes pulse {
    0%, 100% {
      border-color: ${theme.colors.success};
    }
    50% {
      border-color: rgba(34, 197, 94, 0.5);
    }
  }
`;

const Controls = styled.div`
  position: absolute;
  bottom: ${theme.spacing.md};
  left: ${theme.spacing.md};
  right: ${theme.spacing.md};
  display: flex;
  gap: ${theme.spacing.sm};
  justify-content: center;
`;

const Button = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: background-color ${theme.transitions.fast};

  &:hover {
    background-color: ${theme.colors.primaryDark};
  }

  &:disabled {
    background-color: ${theme.colors.borderDark};
    cursor: not-allowed;
  }
`;

export function CameraView({ onScan, onError }: CameraViewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const scannerRef = useRef<BarcodeScanner | null>(null);
  const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);
  const [currentCameraIndex, setCurrentCameraIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [loadingMessage, setLoadingMessage] = useState('Initializing camera...');

  useEffect(() => {
    let mounted = true;

    const initScanner = async () => {
      if (!videoRef.current) return;

      try {
        // Check if camera is supported first
        if (!BarcodeScanner.isSupported()) {
          throw new Error(
            'Camera access requires HTTPS or localhost. Please use a secure connection.'
          );
        }

        setLoadingMessage('Requesting camera permission...');

        const scanner = new BarcodeScanner({
          onScan,
          onError,
          throttleMs: 800,
        });

        scannerRef.current = scanner;

        setLoadingMessage('Loading cameras...');

        const availableCameras = await scanner.listCameras();
        if (mounted) {
          setCameras(availableCameras);

          if (availableCameras.length === 0) {
            throw new Error('No cameras found on this device');
          }

          // Find environment camera index
          const envIndex = availableCameras.findIndex((cam) =>
            cam.label.toLowerCase().includes('back') ||
            cam.label.toLowerCase().includes('environment')
          );
          const initialIndex = envIndex >= 0 ? envIndex : 0;
          setCurrentCameraIndex(initialIndex);

          setLoadingMessage('Starting camera...');

          if (availableCameras.length > 0) {
            await scanner.start(
              videoRef.current,
              availableCameras[initialIndex]?.deviceId
            );
          }
          setIsLoading(false);
        }
      } catch (error) {
        if (mounted) {
          setIsLoading(false);
          if (onError && error instanceof Error) {
            onError(error);
          }
        }
      }
    };

    initScanner();

    return () => {
      mounted = false;
      if (scannerRef.current) {
        scannerRef.current.stop();
      }
    };
  }, [onScan, onError]);

  const switchCamera = async () => {
    if (!scannerRef.current || cameras.length <= 1) return;

    const nextIndex = (currentCameraIndex + 1) % cameras.length;
    setCurrentCameraIndex(nextIndex);

    try {
      await scannerRef.current.switchCamera(cameras[nextIndex].deviceId);
    } catch (error) {
      if (onError && error instanceof Error) {
        onError(error);
      }
    }
  };

  return (
    <Container>
      <Video 
        ref={videoRef} 
        autoPlay 
        playsInline 
        muted 
        aria-label="Barcode and QR code scanner camera view"
      />
      {isLoading ? (
        <LoadingOverlay>
          <div style={{ fontSize: '2rem' }}>📷</div>
          <LoadingText>{loadingMessage}</LoadingText>
        </LoadingOverlay>
      ) : (
        <>
          <Overlay>
            <ScanLine aria-hidden="true" />
          </Overlay>
          {cameras.length > 1 && (
            <Controls>
              <Button onClick={switchCamera} aria-label="Switch camera">
                🔄 Switch Camera
              </Button>
            </Controls>
          )}
        </>
      )}
    </Container>
  );
}

