from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .machine import Machine


def fcfs(self: Machine) -> int:
    if self.responses:
        selected = self.responses[0]
        for r in self.responses:
            if r["body"]["submitted_at"] < selected["body"]["submitted_at"]:  # type: ignore
                selected = r
        return selected["from_agent"]
    return -1


def lpt(self: Machine) -> int:
    if self.responses:
        selected = self.responses[0]
        for r in self.responses:
            if r["body"]["print_time"] > selected["body"]["print_time"]:  # type: ignore
                selected = r
        return selected["from_agent"]
    return -1


def spt(self: Machine) -> int:
    if self.responses:
        selected = self.responses[0]
        for r in self.responses:
            if r["body"]["print_time"] < selected["body"]["print_time"]:  # type: ignore
                selected = r
        return selected["from_agent"]
    return -1


def frfs(self: Machine) -> int:
    if self.responses:
        return self.responses[0]["from_agent"]
    return -1


def randomly_select(self: Machine) -> int:
    if self.responses:
        # Fixed random state.
        r = np.random.RandomState(seed=self.id)
        selected = r.choice(self.responses)  # type: ignore
        return selected["from_agent"]
    return -1
