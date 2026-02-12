"""
RFID Scan API Endpoints

Provides endpoints for:
- Starting/stopping active RFID scanning
- Single inventory scan (get all tags in range)
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from prisma.models import User
from pydantic import BaseModel

from app.api.dependencies.auth import get_current_user
from app.core.permissions import requires_any_role
from app.db.prisma import prisma_client
from app.services.rfid_reader import rfid_reader_service
from app.services.tag_listener_service import tag_listener_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rfid-scan", tags=["rfid-scan"])


class TagResponse(BaseModel):
    """Tag data from inventory scan."""

    epc: str
    rssi: Optional[float] = None
    antenna_port: Optional[int] = None
    pc: Optional[int] = None
    timestamp: Optional[str] = None
    is_mapped: bool = False
    target_qr: Optional[str] = None


class ScanStatusResponse(BaseModel):
    """Scan status response."""

    is_connected: bool
    is_scanning: bool
    reader_ip: str
    reader_port: int


class InventoryResponse(BaseModel):
    """Inventory scan response."""

    success: bool
    tag_count: int
    tags: List[TagResponse]
    message: str


@router.get("/status", response_model=ScanStatusResponse)
async def get_scan_status(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Get current RFID scanner status."""
    return ScanStatusResponse(
        is_connected=rfid_reader_service.is_connected,
        is_scanning=rfid_reader_service.is_scanning or tag_listener_service.is_scanning,
        reader_ip=rfid_reader_service.reader_ip,
        reader_port=rfid_reader_service.reader_port,
    )


@router.get("/available")
async def get_available_tags(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """
    Get recent tags that are NOT linked to any product (productId is NULL).
    """
    # 1. Get recent raw scans from listener memory
    recent_scans = tag_listener_service.get_recent_tags(count=100)
    logger.info(f"get_available_tags: Found {len(recent_scans)} recent scans")
    
    if not recent_scans:
        return []

    # 2. Extract EPCs
    epcs = [t['epc'] for t in recent_scans if t.get('epc')]
    
    # 3. Find which of these EPCs are already linked in DB
    # We want to filter OUT tags that have a productId
    db_tags = await prisma_client.client.rfidtag.find_many(
        where={
            "epc": {"in": epcs},
            "productId": {"not": None}
        }
    )
    
    linked_epcs = {t.epc for t in db_tags}
    logger.info(f"get_available_tags: Found {len(linked_epcs)} linked tags")

    # 4. Filter and Format
    available = []
    seen_epcs = set()
    
    for scan in recent_scans:
        epc = scan.get('epc')
        if epc and epc not in linked_epcs and epc not in seen_epcs:
            # Check if tag exists in DB at all (optional, but good for consistent ID)
            # For now, we use EPC as ID for unlinked tags in the UI
            available.append({
                "id": epc, 
                "epc": epc,
                "rssi": scan.get('rssi'),
                "scannedAt": scan.get('timestamp')
            })
            seen_epcs.add(epc)
            
    logger.info(f"get_available_tags: Returning {len(available)} available tags")
    return available


@router.post("/connect")
async def connect_reader(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Connect to the RFID reader."""
    if rfid_reader_service.is_connected:
        return {"status": "already_connected", "message": "Already connected to reader"}

    success = await rfid_reader_service.connect()
    if success:
        return {
            "status": "connected",
            "message": "Successfully connected to RFID reader",
        }
    else:
        raise HTTPException(status_code=503, detail="Failed to connect to RFID reader")


@router.post("/disconnect")
async def disconnect_reader(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Disconnect from the RFID reader."""
    await rfid_reader_service.disconnect()
    return {"status": "disconnected", "message": "Disconnected from RFID reader"}


@router.post("/start")
async def start_scanning(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Start continuous RFID scanning."""
    # Check if passive listener is already running (preferred mode)
    if tag_listener_service._running:
        logger.info("Passive listener running - sending Start Inventory command")
        success = tag_listener_service.start_scan()
        
        if not success:
            logger.warning("Passive listener active but no reader connected")
            raise HTTPException(
                status_code=503, 
                detail="Reader not connected to listener service. Please check device connection."
            )

        return {
            "status": "scanning", 
            "mode": "passive_active_control", 
            "message": "Started continuous scanning (Answer Mode)"
        }

    # Fall back to active mode
    if not rfid_reader_service.is_connected:
        # Try to connect first
        success = await rfid_reader_service.connect()
        if not success:
            raise HTTPException(status_code=503, detail="Cannot connect to RFID reader")

    await rfid_reader_service.start_scanning()
    return {
        "status": "scanning",
        "mode": "active",
        "message": "Started continuous scanning",
    }


@router.post("/stop")
async def stop_scanning(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Stop continuous RFID scanning."""
    # Try stopping passive listener command too
    try:
        if tag_listener_service._running:
            tag_listener_service.stop_scan()
    except Exception as e:
        logger.error(f"Error stopping tag listener service: {e}")

    try:
        await rfid_reader_service.stop_scanning()
    except Exception as e:
        logger.error(f"Error stopping RFID reader service: {e}")
        
    return {"status": "stopped", "message": "Stopped scanning"}


@router.post("/inventory", response_model=InventoryResponse)
async def perform_inventory(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """
    Perform a single inventory scan and return all tags in range.

    This sends the Inventory command to the reader and waits for the response
    containing all detected tags.
    """
    if not rfid_reader_service.is_connected:
        # Try to connect first
        success = await rfid_reader_service.connect()
        if not success:
            raise HTTPException(status_code=503, detail="Cannot connect to RFID reader")

    try:
        tags = await rfid_reader_service.read_single_tag()

        # Check mapping status for each tag

        tag_responses = []
        for tag in tags:
            epc = tag.get("epc", "")
            is_mapped = False
            target_qr = None

            try:
                mapping = await prisma_client.client.tagmapping.find_unique(where={"epc": epc})
                if mapping:
                    is_mapped = True
                    target_qr = mapping.encryptedQr
            except Exception as e:
                logger.warning(f"Error checking mapping for {epc}: {e}")

            tag_responses.append(
                TagResponse(
                    epc=epc,
                    rssi=tag.get("rssi"),
                    antenna_port=tag.get("antenna_port"),
                    pc=tag.get("pc"),
                    timestamp=tag.get("timestamp"),
                    is_mapped=is_mapped,
                    target_qr=target_qr,
                )
            )

        return InventoryResponse(
            success=True,
            tag_count=len(tag_responses),
            tags=tag_responses,
            message=(f"Found {len(tag_responses)} tag(s)" if tag_responses else "No tags found"),
        )

    except Exception as e:
        logger.error(f"Inventory failed: {e}")
        raise HTTPException(status_code=500, detail=f"Inventory failed: {str(e)}")


# =============================================================================
# HIGH PRIORITY - Module Control
# =============================================================================


class PowerRequest(BaseModel):
    power_dbm: int  # 0-30


class MemoryReadRequest(BaseModel):
    mem_bank: int  # 0=Reserved, 1=EPC, 2=TID, 3=User
    start_addr: int = 0
    word_count: int = 6


@router.post("/initialize")
async def initialize_device(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])),
):
    """Initialize/reset the RFID reader."""
    success = await rfid_reader_service.initialize_device()
    if success:
        return {"status": "initialized", "message": "Device initialized successfully"}
    raise HTTPException(status_code=500, detail="Failed to initialize device")


@router.post("/power")
async def set_power(
    request: PowerRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])),
):
    """Set RF output power (0-30 dBm)."""
    if not 0 <= request.power_dbm <= 30:
        raise HTTPException(status_code=400, detail="Power must be 0-30 dBm")

    success = await rfid_reader_service.set_power(request.power_dbm)
    if success:
        return {"status": "success", "power_dbm": request.power_dbm}
    raise HTTPException(status_code=500, detail="Failed to set power")


@router.post("/read-memory")
async def read_tag_memory(
    request: MemoryReadRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Read tag memory bank (TID, User, etc)."""
    data = await rfid_reader_service.read_tag_memory(
        request.mem_bank, request.start_addr, request.word_count
    )
    if data:
        return {"success": True, "data": data.hex().upper(), "length": len(data)}
    raise HTTPException(status_code=500, detail="Failed to read tag memory")


# =============================================================================
# MEDIUM PRIORITY - Configuration
# =============================================================================


class NetworkRequest(BaseModel):
    ip: str
    subnet: str = "255.255.255.0"
    gateway: str = "192.168.1.1"
    port: int = 4001


class RssiFilterRequest(BaseModel):
    antenna: int  # 1-4
    threshold: int  # 0-255


@router.get("/network")
async def get_network(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])),
):
    """Get current network configuration."""
    config = await rfid_reader_service.get_network_config()
    return config


@router.post("/network")
async def set_network(
    request: NetworkRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN"])),
):
    """Set network configuration. Requires device restart to take effect."""
    success = await rfid_reader_service.set_network_config(
        request.ip, request.subnet, request.gateway, request.port
    )
    if success:
        return {
            "status": "success",
            "message": "Network config set. Restart device to apply.",
        }
    raise HTTPException(status_code=500, detail="Failed to set network config")


@router.post("/rssi-filter")
async def set_rssi_filter(
    request: RssiFilterRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])),
):
    """Set RSSI filter threshold for antenna."""
    success = await rfid_reader_service.set_rssi_filter(request.antenna, request.threshold)
    if success:
        return {
            "status": "success",
            "antenna": request.antenna,
            "threshold": request.threshold,
        }
    raise HTTPException(status_code=500, detail="Failed to set RSSI filter")


@router.get("/config")
async def get_all_config(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])),
):
    """Get all device parameters."""
    params = await rfid_reader_service.get_all_params()
    return params


# =============================================================================
# GPIO Control
# =============================================================================


class GpioRequest(BaseModel):
    pin: int  # 1-4
    direction: int  # 0=Input, 1=Output
    level: int = 0  # 0=Low, 1=High


@router.get("/gpio/levels")
async def get_gpio_levels(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])),
):
    """Get current GPIO pin levels."""
    levels = await rfid_reader_service.get_gpio_levels()
    return {"gpio": levels}


@router.post("/gpio/config")
async def set_gpio(
    request: GpioRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN"])),
):
    """Configure GPIO pin."""
    success = await rfid_reader_service.set_gpio(request.pin, request.direction, request.level)
    if success:
        return {"status": "success", "pin": request.pin}
    raise HTTPException(status_code=500, detail="Failed to configure GPIO")


# =============================================================================
# Relay Control
# =============================================================================


class RelayRequest(BaseModel):
    close: bool = True


@router.post("/relay/{relay_num}")
async def control_relay(
    relay_num: int,
    request: RelayRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Control relay 1 or 2."""
    if relay_num not in [1, 2]:
        raise HTTPException(status_code=400, detail="Relay must be 1 or 2")

    success = await rfid_reader_service.control_relay(relay_num, request.close)
    if success:
        return {"status": "success", "relay": relay_num, "closed": request.close}
    raise HTTPException(status_code=500, detail="Failed to control relay")


# =============================================================================
# Gate Control
# =============================================================================


class GateConfigRequest(BaseModel):
    mode: int = 1  # 0=disabled, 1=enabled
    sensitivity: int = 80  # 0-255
    direction_detect: bool = True


@router.get("/gate/status")
async def get_gate_status(
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Get gate detection status."""
    status = await rfid_reader_service.get_gate_status()
    return status


@router.post("/gate/config")
async def set_gate_config(
    request: GateConfigRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])),
):
    """Configure gate detection mode."""
    success = await rfid_reader_service.set_gate_config(
        request.mode, request.sensitivity, request.direction_detect
    )
    if success:
        return {"status": "success", "message": "Gate config updated"}
    raise HTTPException(status_code=500, detail="Failed to set gate config")


# =============================================================================
# Query & Select Commands
# =============================================================================


class QueryParamRequest(BaseModel):
    q_value: int = 4  # 0-15
    session: int = 0  # 0-3
    target: int = 0  # 0=A, 1=B


class SelectTagRequest(BaseModel):
    epc_mask: str  # Hex string


@router.post("/query-params")
async def set_query_params(
    request: QueryParamRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])),
):
    """Set Query command parameters for inventory optimization."""
    success = await rfid_reader_service.set_query_params(
        request.q_value, request.session, request.target
    )
    if success:
        return {"status": "success", "q_value": request.q_value}
    raise HTTPException(status_code=500, detail="Failed to set query params")


@router.post("/select-tag")
async def select_tag(
    request: SelectTagRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER", "EMPLOYEE"])),
):
    """Select specific tag for subsequent operations."""
    success = await rfid_reader_service.select_tag(request.epc_mask)
    if success:
        return {"status": "success", "epc_mask": request.epc_mask}
    raise HTTPException(status_code=500, detail="Failed to select tag")
