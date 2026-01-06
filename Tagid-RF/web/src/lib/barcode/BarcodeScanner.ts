import { BrowserMultiFormatReader, Result } from '@zxing/library';

export interface BarcodeScannerConfig {
  onScan: (barcode: string) => void;
  onError?: (error: Error) => void;
  throttleMs?: number;
  preferredCamera?: 'environment' | 'user';
}

export class BarcodeScanner {
  private reader: BrowserMultiFormatReader;
  private videoElement: HTMLVideoElement | null = null;
  private lastScanTime = 0;
  private throttleMs: number;
  private onScan: (barcode: string) => void;
  private onError?: (error: Error) => void;
  private isScanning = false;
  private currentDeviceId: string | null = null;

  constructor(config: BarcodeScannerConfig) {
    // BrowserMultiFormatReader supports multiple barcode formats including:
    // - QR Code, Data Matrix (2D barcodes)
    // - EAN-8, EAN-13, UPC-A, UPC-E (product barcodes)
    // - Code 39, Code 93, Code 128, ITF, Codabar (1D barcodes)
    this.reader = new BrowserMultiFormatReader();
    this.onScan = config.onScan;
    this.onError = config.onError;
    this.throttleMs = config.throttleMs ?? 800;
  }

  /**
   * Check if the environment supports camera access
   */
  static isSupported(): boolean {
    return !!(
      typeof navigator !== 'undefined' &&
      navigator.mediaDevices &&
      typeof navigator.mediaDevices.getUserMedia === 'function' &&
      (window.isSecureContext || window.location.hostname === 'localhost')
    );
  }

  /**
   * Request camera permissions explicitly
   */
  async requestPermissions(): Promise<boolean> {
    try {
      // Request permission by attempting to get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      });
      // Stop the stream immediately after getting permission
      stream.getTracks().forEach((track) => track.stop());
      return true;
    } catch (error) {
      if (error instanceof Error) {
        // More specific error messages
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
          throw new Error('Camera permission denied. Please allow camera access in your browser settings.');
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
          throw new Error('No camera found on this device.');
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
          throw new Error('Camera is already in use by another application.');
        } else if (error.name === 'OverconstrainedError') {
          throw new Error('Camera does not support the required constraints.');
        } else if (error.name === 'NotSupportedError') {
          throw new Error('Camera access is not supported on this device or browser.');
        } else if (error.name === 'SecurityError') {
          throw new Error('Camera access requires HTTPS or localhost. Please use a secure connection.');
        }
      }
      throw new Error('Failed to access camera: ' + (error as Error).message);
    }
  }

  async listCameras(): Promise<MediaDeviceInfo[]> {
    try {
      const devices = await this.reader.listVideoInputDevices();
      return devices;
    } catch (error) {
      this.handleError(
        error instanceof Error ? error : new Error('Failed to list cameras')
      );
      return [];
    }
  }

  async start(
    videoElement: HTMLVideoElement,
    deviceId?: string
  ): Promise<void> {
    if (this.isScanning) {
      await this.stop();
    }

    // Check if camera is supported
    if (!BarcodeScanner.isSupported()) {
      const error = new Error(
        'Camera access is not supported. Please use HTTPS or localhost.'
      );
      this.handleError(error);
      throw error;
    }

    this.videoElement = videoElement;
    this.isScanning = true;

    try {
      // Request permissions first if no device specified
      if (!deviceId) {
        await this.requestPermissions();
      }

      // If no deviceId provided, try to find the environment-facing camera
      let selectedDeviceId = deviceId;
      if (!selectedDeviceId) {
        const devices = await this.listCameras();
        
        if (devices.length === 0) {
          throw new Error('No cameras found on this device');
        }

        // Try to find back/environment camera
        const environmentCamera = devices.find((device) =>
          device.label.toLowerCase().includes('back') ||
          device.label.toLowerCase().includes('environment')
        );
        selectedDeviceId = environmentCamera?.deviceId || devices[0]?.deviceId;
      }

      if (!selectedDeviceId) {
        throw new Error('No camera available');
      }

      this.currentDeviceId = selectedDeviceId;

      // Start continuous decode
      await this.reader.decodeFromVideoDevice(
        selectedDeviceId,
        videoElement,
        (result: Result | null, error?: Error) => {
          if (result) {
            this.handleScan(result);
          }
          // Filter out expected "not found" errors - these occur when no barcode is visible
          if (error && !this.isNotFoundError(error)) {
            this.handleError(error);
          }
        }
      );
    } catch (error) {
      this.isScanning = false;
      this.handleError(
        error instanceof Error ? error : new Error('Failed to start scanner')
      );
      throw error;
    }
  }

  async stop(): Promise<void> {
    if (!this.isScanning) return;

    this.isScanning = false;
    this.reader.reset();

    if (this.videoElement) {
      const stream = this.videoElement.srcObject as MediaStream;
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
      this.videoElement.srcObject = null;
      this.videoElement = null;
    }

    this.currentDeviceId = null;
  }

  async switchCamera(deviceId: string): Promise<void> {
    if (!this.videoElement) {
      throw new Error('Scanner not started');
    }

    await this.start(this.videoElement, deviceId);
  }

  getCurrentDeviceId(): string | null {
    return this.currentDeviceId;
  }

  isActive(): boolean {
    return this.isScanning;
  }

  private handleScan(result: Result): void {
    const now = Date.now();
    if (now - this.lastScanTime < this.throttleMs) {
      return; // Throttle duplicate scans
    }

    this.lastScanTime = now;
    const barcode = result.getText();
    this.onScan(barcode);

    // Vibrate if supported
    if ('vibrate' in navigator) {
      navigator.vibrate(100);
    }
  }

  private isNotFoundError(error: Error): boolean {
    // Check if this is an expected "barcode not found" error
    return (
      error.name === 'NotFoundException' ||
      error.message.includes('No MultiFormat Readers') ||
      error.message.includes('not found') ||
      error.message.includes('Not found')
    );
  }

  private handleError(error: Error): void {
    if (this.onError) {
      this.onError(error);
    }
  }
}

