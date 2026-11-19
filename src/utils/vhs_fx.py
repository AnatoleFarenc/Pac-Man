"""CRT/VHS post-processing effects applied to the pygame screen surface."""

import random
import pygame


def apply_crt_effect(
        screen: pygame.Surface,
        time: float,
        intensity: str = "minimum",
        pixelation: str = "minimum"
) -> None:
    """Apply a set of CRT effects (scanlines, glow, glitch) to
    *screen* in-place.

    Args:
        screen: The pygame surface to modify.
        time: Accumulated game time used to animate scrolling scanlines.
        intensity: Glitch intensity level — ``"minimum"``, ``"medium"``, or
            ``"maximum"``.
        pixelation: Pixelation level (currently unused;
        reserved for future use).
    """

    _apply_scanlines(screen, time)
    # _apply_pixelation(screen, pixelation=pixelation)
    # _apply_flicker(screen)
    _apply_glow(screen)
    _apply_vhs_glitch(screen, intensity=intensity)


def _apply_scanlines(screen: pygame.Surface, time: float) -> None:
    """Draw scrolling horizontal scanlines over *screen*.

    Args:
        screen: Target pygame surface.
        time: Accumulated game time used to offset the scanline start position.
    """

    start = int((time*50) % 4)
    width, height = screen.get_size()
    scanline_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    for y in range(start, height, 4):
        pygame.draw.line(scanline_surface, (0, 0, 0, 50), (0, y), (width, y))
    screen.blit(scanline_surface, (0, 0))


def _apply_pixelation(screen: pygame.Surface, pixelation: str) -> None:
    """Downscale and upscale *screen* to simulate a pixel-art look.

    Args:
        screen: Target pygame surface (modified in-place).
        pixelation: Reduction factor — ``"minimum"`` (÷2), ``"medium"`` (÷4),
            or ``"maximum"`` (÷6).
    """

    pixelation_ratio = {"minimum": 2, "medium": 4, "maximum": 6}.get(
        pixelation, 2)
    width, height = screen.get_size()
    small_surf = pygame.transform.scale(
        screen, (width // pixelation_ratio, height // pixelation_ratio)
    )
    screen.blit(pygame.transform.scale(small_surf, (width, height)), (0, 0))


def _apply_flicker(screen: pygame.Surface) -> None:
    """Randomly apply a subtle white flash to simulate screen flicker.

    Args:
        screen: Target pygame surface (modified in-place).
    """

    if random.randint(0, 20) == 0:
        flicker_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        flicker_surface.fill((255, 255, 255, 5))
        screen.blit(flicker_surface, (0, 0))


def _apply_glow(screen: pygame.Surface) -> None:
    """Blend a blurred copy of *screen* onto itself to
    create a bloom/glow effect.

    Args:
        screen: Target pygame surface (modified in-place).
    """

    width, height = screen.get_size()

    # Create a blurred surface
    glow_surf = pygame.transform.smoothscale(screen, (width // 3, height // 3))
    glow_surf = pygame.transform.smoothscale(glow_surf, (width, height))

    # Overlay with transparency
    glow_surf.set_alpha(100)
    screen.blit(glow_surf, (0, 0))


def _apply_vhs_glitch(screen: pygame.Surface, intensity: str) -> None:
    """Apply VHS-style glitch artefacts (slice shift, colour bleed, static).

    Args:
        screen: Target pygame surface (modified in-place).
        intensity: Glitch intensity — ``"minimum"``,
        ``"medium"``, or ``"maximum"``.
    """

    width, height = screen.get_size()
    glitch_surface = screen.copy()

    glitch_count = {"minimum": 2, "medium": 4, "maximum": 8}.get(intensity, 4)

    for _ in range(glitch_count):
        _add_glitch_effect(height, width, glitch_surface, intensity)

    _add_color_separation(screen, glitch_surface, intensity)
    _add_rolling_static(screen, height, width, intensity)

    screen.blit(glitch_surface, (0, 0))


def _add_glitch_effect(
        height: int,
        width: int,
        glitch_surface: pygame.Surface,
        intensity: str
) -> None:
    """Randomly shift a horizontal slice of *glitch_surface* by a pixel offset.

    Args:
        height: Height of the surface in pixels.
        width: Width of the surface in pixels.
        glitch_surface: Surface to modify in-place.
        intensity: Controls the maximum horizontal shift amount.
    """

    shift_amount = {"minimum": 10, "medium": 20, "maximum": 40}.get(
        intensity, 20)

    if random.random() < 0.05:
        y_start = random.randint(0, height - 20)
        slice_height = random.randint(5, 20)
        offset = random.randint(-shift_amount, shift_amount)

        slice_area = pygame.Rect(0, y_start, width, slice_height)
        slice_copy = glitch_surface.subsurface(slice_area).copy()
        glitch_surface.blit(slice_copy, (offset, y_start))


def _add_color_separation(
        screen: pygame.Surface,
        glitch_surface: pygame.Surface,
        intensity: str
) -> None:
    """Randomly add RGB channel bleed by blitting
    shifted copies of the surface.

    Args:
        screen: Target pygame surface (modified in-place via additive blend).
        glitch_surface: Source surface used as the colour-shift reference.
        intensity: Controls the maximum channel offset in pixels.
    """

    color_shift = {"minimum": 2, "medium": 6, "maximum": 10}.get(intensity, 4)

    if random.random() < 0.05:
        for i in range(3):
            x_offset = random.randint(-color_shift, color_shift)
            y_offset = random.randint(-color_shift, color_shift)
            color_shift_surface = glitch_surface.copy()
            color_shift_surface.fill((0, 0, 0))
            color_shift_surface.blit(glitch_surface, (x_offset, y_offset))
            screen.blit(
                color_shift_surface, (0, 0), special_flags=pygame.BLEND_ADD)


def _add_rolling_static(
        screen: pygame.Surface,
        height: int,
        width: int,
        intensity: str
) -> None:
    """Draw translucent horizontal static lines over
    *screen* at random positions.

    Args:
        screen: Target pygame surface (modified in-place via additive blend).
        height: Height of the surface in pixels.
        width: Width of the surface in pixels.
        intensity: Controls how frequently static lines appear.
    """

    static_chance = {"minimum": 0.1, "medium": 0.3, "maximum": 0.8}.get(
        intensity, 0.2)

    static_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 8):
        if random.random() < static_chance:
            pygame.draw.line(
                static_surface,
                (255, 255, 255, random.randint(30, 80)),
                (0, y),
                (width, y)
                )

    screen.blit(static_surface, (0, 0), special_flags=pygame.BLEND_ADD)
