from dataclasses import dataclass, field


@dataclass(frozen=True)
class Channel:
    url: str
    name: str
    tvg_id: str = field(default="")
    tvg_name: str = field(default="")
    tvg_logo: str = field(default="")
    group: str = field(default="")
