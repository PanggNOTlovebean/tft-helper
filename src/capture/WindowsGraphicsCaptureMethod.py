# original https://github.com/dantmnf & https://github.com/hakaboom/winAuto
import ctypes
import ctypes.wintypes
import platform
import sys
import time
import cv2
import numpy as np
from typing_extensions import override
from pathlib import Path
from time import sleep

from __version__ import APP_START_TIME, ENABLE_SAVE_SCREENSHOT, SCREENSHOT_BASE_DIR
from capture.hwnd_window import HwndWindow
from capture import d3d11
from capture.BaseWindowsCaptureMethod import BaseWindowsCaptureMethod
from capture.utils import WINDOWS_BUILD_NUMBER

PBYTE = ctypes.POINTER(ctypes.c_ubyte)
WGC_NO_BORDER_MIN_BUILD = 20348
WGC_MIN_BUILD = 19041
#  导入logging
from loguru import logger as log

class WindowsGraphicsCaptureMethod(BaseWindowsCaptureMethod):
    name = "Windows Graphics Capture"
    description = "fast, most compatible, capped at 60fps"
    
    def __init__(self, hwnd_window: HwndWindow):
        super().__init__(hwnd_window)
        self.last_frame = None
        self.last_frame_time = 0
        self.frame_pool = None
        self.item = None
        self.session = None
        self.cputex = None
        self.rtdevice = None
        self.dxdevice = None
        self.start_or_stop()

    def frame_arrived_callback(self, x, y):
        try:
            self.last_frame_time = time.time()
            next_frame = self.frame_pool.TryGetNextFrame()
            if next_frame is not None:
                self.last_frame = self.convert_dx_frame(next_frame)
            else:
                log.warning('frame_arrived_callback TryGetNextFrame returned None')
        except Exception as e:
            import traceback
            traceback.print_exc()
            log.error(f"TryGetNextFrame error {e}")
            self.close()
            return

    def convert_dx_frame(self, frame):
        if not frame:
            log.warning('convert_dx_frame self.last_dx_frame is none')
            return None
        need_reset_framepool = False
        if frame.ContentSize.Width != self.last_size.Width or frame.ContentSize.Height != self.last_size.Height:
            need_reset_framepool = True
            self.last_size = frame.ContentSize

        if need_reset_framepool:
            log.info('need_reset_framepool')
            self.reset_framepool(frame.ContentSize)
            return
        need_reset_device = False
        tex = None
        cputex = None
        try:
            from rotypes.Windows.Graphics.DirectX.Direct3D11 import IDirect3DDxgiInterfaceAccess
            from rotypes.roapi import GetActivationFactory
            tex = frame.Surface.astype(IDirect3DDxgiInterfaceAccess).GetInterface(
                d3d11.ID3D11Texture2D.GUID).astype(d3d11.ID3D11Texture2D)
            desc = tex.GetDesc()
            desc2 = d3d11.D3D11_TEXTURE2D_DESC()
            desc2.Width = desc.Width
            desc2.Height = desc.Height
            desc2.MipLevels = desc.MipLevels
            desc2.ArraySize = desc.ArraySize
            desc2.Format = desc.Format
            desc2.SampleDesc = desc.SampleDesc
            desc2.Usage = d3d11.D3D11_USAGE_STAGING
            desc2.CPUAccessFlags = d3d11.D3D11_CPU_ACCESS_READ
            desc2.BindFlags = 0
            desc2.MiscFlags = 0
            cputex = self.dxdevice.CreateTexture2D(ctypes.byref(desc2), None)
            self.immediatedc.CopyResource(cputex, tex)
            mapinfo = self.immediatedc.Map(cputex, 0, d3d11.D3D11_MAP_READ, 0)
            img = np.ctypeslib.as_array(ctypes.cast(mapinfo.pData, PBYTE),
                                        (desc.Height, mapinfo.RowPitch // 4, 4))[
                  :, :desc.Width].copy()
            self.immediatedc.Unmap(cputex, 0)
            # log.debug(f'frame latency {(time.time() - start):.3f} {(time.time() - dx_time):.3f}')
            return img
        except OSError as e:
            if e.winerror == d3d11.DXGI_ERROR_DEVICE_REMOVED or e.winerror == d3d11.DXGI_ERROR_DEVICE_RESET:
                need_reset_framepool = True
                need_reset_device = True
                log.error('convert_dx_frame win error', e)
            else:
                raise e
        finally:
            if tex is not None:
                tex.Release()
            if cputex is not None:
                cputex.Release()
        if need_reset_framepool:
            self.reset_framepool(frame.ContentSize, need_reset_device)
            return self.get_frame()

    @property
    def hwnd_window(self):
        return self._hwnd_window

    @hwnd_window.setter
    def hwnd_window(self, hwnd_window):
        self._hwnd_window = hwnd_window
        self.start_or_stop()

    def connected(self):
        return self.hwnd_window is not None and self.hwnd_window.exists and self.frame_pool is not None

    def start_or_stop(self, capture_cursor=True):
        if self.hwnd_window.hwnd and self.hwnd_window.exists and self.frame_pool is None:
            try:
                from rotypes import IInspectable
                from rotypes.Windows.Foundation import TypedEventHandler
                from rotypes.Windows.Graphics.Capture import Direct3D11CaptureFramePool, IGraphicsCaptureItemInterop, \
                    IGraphicsCaptureItem, GraphicsCaptureItem
                from rotypes.Windows.Graphics.DirectX import DirectXPixelFormat
                from rotypes.Windows.Graphics.DirectX.Direct3D11 import IDirect3DDevice, \
                    CreateDirect3D11DeviceFromDXGIDevice, \
                    IDirect3DDxgiInterfaceAccess
                from rotypes.roapi import GetActivationFactory
                log.info('init windows capture')
                interop = GetActivationFactory('Windows.Graphics.Capture.GraphicsCaptureItem').astype(
                    IGraphicsCaptureItemInterop)
                self.rtdevice = IDirect3DDevice()
                self.dxdevice = d3d11.ID3D11Device()
                self.immediatedc = d3d11.ID3D11DeviceContext()
                self.create_device()
                item = interop.CreateForWindow(self.hwnd_window.hwnd, IGraphicsCaptureItem.GUID)
                self.item = item
                self.last_size = item.Size
                delegate = TypedEventHandler(GraphicsCaptureItem, IInspectable).delegate(
                    self.close)
                self.evtoken = item.add_Closed(delegate)
                self.frame_pool = Direct3D11CaptureFramePool.CreateFreeThreaded(self.rtdevice,
                                                                                DirectXPixelFormat.B8G8R8A8UIntNormalized,
                                                                                1, item.Size)
                self.session = self.frame_pool.CreateCaptureSession(item)
                pool = self.frame_pool
                pool.add_FrameArrived(
                    TypedEventHandler(Direct3D11CaptureFramePool, IInspectable).delegate(
                        self.frame_arrived_callback))
                self.session.IsCursorCaptureEnabled = capture_cursor
                if WINDOWS_BUILD_NUMBER >= WGC_NO_BORDER_MIN_BUILD:
                    self.session.IsBorderRequired = False
                self.session.StartCapture()
                while self.last_frame_time <= 0:
                    # 等待直到session初始化首帧时间
                    log.info('wait for first frame')
                    sleep(0.1)
                return True
            except Exception as e:
                log.error(f'start_or_stop failed: {self.hwnd_window}')
                return False
        elif not self.hwnd_window.exists and self.frame_pool is not None:
            self.close()
            return False
        return self.hwnd_window.exists

    def create_device(self):
        from rotypes.Windows.Graphics.DirectX.Direct3D11 import CreateDirect3D11DeviceFromDXGIDevice
        d3d11.D3D11CreateDevice(
            None,
            d3d11.D3D_DRIVER_TYPE_HARDWARE,
            None,
            d3d11.D3D11_CREATE_DEVICE_BGRA_SUPPORT,
            None,
            0,
            d3d11.D3D11_SDK_VERSION,
            ctypes.byref(self.dxdevice),
            None,
            ctypes.byref(self.immediatedc)
        )
        self.rtdevice = CreateDirect3D11DeviceFromDXGIDevice(self.dxdevice)
        self.evtoken = None

    @override
    def close(self):
        log.info('destroy windows capture')
        if self.frame_pool is not None:
            self.frame_pool.Close()
            self.frame_pool = None
        if self.session is not None:
            self.session.Close()  # E_UNEXPECTED ???
            self.session = None
        self.item = None
        if self.rtdevice:
            self.rtdevice.Release()
        if self.dxdevice:
            self.dxdevice.Release()
        if self.cputex:
            self.cputex.Release()

    @override
    def do_get_frame(self):
        # 检查捕获是否可以开始或停止
        if self.start_or_stop():
            frame = self.last_frame  # 获取最后捕获的帧
            frame_time = self.last_frame_time
            self.last_frame = None  # 重置 last_frame 以便下次捕获
            if frame is None:  # 如果没有可用的帧
                cur_time = time.time()
                if  cur_time - self.last_frame_time > 10:  # 检查是否超过 10 秒没有帧
                    log.warning(f'no frame for 60 sec, try to restart')
                    self.close()  # 关闭捕获会话
                    self.last_frame_time = time.time()  # 更新最后帧时间
                    return self.do_get_frame()  # 重试获取帧
                else:
                    return None  # 如果没有帧，返回 None
            ping = time.time() - self.last_frame_time  # 计算延迟
            if frame is not None:  # 如果帧有效
                new_height, new_width = frame.shape[:2]  # 获取帧的尺寸
                if new_width <= 0 or new_width <= 0:  # 检查尺寸是否无效
                    log.warning(f"get_frame size <=0 {new_width}x{new_height}")
                    frame = None  # 如果无效，将帧设置为 None
            if ping > 2:  # 如果延迟过高
                log.warning(f"latency too large return None frame: {ping}")
                return None  # 返回 None，因延迟过高
            else:
                if ENABLE_SAVE_SCREENSHOT:
                    file_name = f"{int(frame_time - APP_START_TIME):010}.png"
                    cv2.imwrite(SCREENSHOT_BASE_DIR / file_name, frame)
                return frame  # 返回有效的帧

    def reset_framepool(self, size, reset_device=False):
        log.info(f'reset_framepool')
        from rotypes.Windows.Graphics.DirectX import DirectXPixelFormat
        if reset_device:
            self.create_device()
        self.frame_pool.Recreate(self.rtdevice,
                                 DirectXPixelFormat.B8G8R8A8UIntNormalized, 2, size)
    
    def crop_image(self, frame):
        if frame is not None:
            x, y = self.get_crop_point(frame.shape[1], frame.shape[0], self.hwnd_window.width, self.hwnd_window.height)
            if x > 0 or y > 0:
                frame = crop_image(frame, x, y)
        return frame
    
    def get_title_bar_height(self):
        # 获取窗口的边界矩形
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(self._hwnd_window.hwnd, ctypes.byref(rect))
        
        # 获取系统的标题栏高度
        title_bar_height = rect.top - ctypes.windll.user32.GetSystemMetrics(4)  # 4是SM_CYCAPTION
        return title_bar_height

def crop_image(image, border, title_height):
    # Load the image
    # Image dimensions
    height, width = image.shape[:2]

    # Calculate the coordinates for the bottom-right corner
    x2 = width - border
    y2 = height - border

    # Crop the image
    cropped_image = image[title_height:y2, border:x2]

    # print(f"cropped image: {title_height}-{y2}, {border}-{x2} {cropped_image.shape}")
    #
    # cv2.imshow('Image Window', cropped_image)
    #
    # # Wait for any key to be pressed before closing the window
    # cv2.waitKey(0)

    return cropped_image


WINDOWS_BUILD_NUMBER = int(platform.version().split(".")[-1]) if sys.platform == "win32" else -1


def windows_graphics_available():
    log.debug(
        f"check available WINDOWS_BUILD_NUMBER:{WINDOWS_BUILD_NUMBER} >= {WGC_MIN_BUILD} {WINDOWS_BUILD_NUMBER >= WGC_MIN_BUILD}")
    if WINDOWS_BUILD_NUMBER >= WGC_MIN_BUILD:
        try:
            from rotypes.roapi import GetActivationFactory
            from rotypes.Windows.Graphics.Capture import IGraphicsCaptureItemInterop
            GetActivationFactory('Windows.Graphics.Capture.GraphicsCaptureItem').astype(
                IGraphicsCaptureItemInterop)
            return True
        except Exception as e:
            log.error(f'check available failed: {e}', exception=e)
            return False
