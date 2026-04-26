import vlc


class VlcManager:
    _instance: vlc.Instance | None = None

    @classmethod
    def get_instance(cls) -> vlc.Instance:
        """Lazily create and return the shared vlc.Instance."""
        if cls._instance is None:
            cls._instance = vlc.Instance()
        return cls._instance

    @classmethod
    def release(cls) -> None:
        """Release the shared vlc.Instance and reset. Idempotent."""
        if cls._instance is not None:
            cls._instance.release()
            cls._instance = None
