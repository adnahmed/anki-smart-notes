"""
Copyright (C) 2024 Michael Piazza

This file is part of Smart Notes.

Smart Notes is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Smart Notes is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Smart Notes.  If not, see <https://www.gnu.org/licenses/>.
"""


def is_app_legacy() -> bool:
    """Check if the app is running in legacy mode. Always returns False since all subscription functionality has been removed."""
    return False


def is_capacity_remaining(show_box: bool = False) -> bool:
    """Check if capacity is remaining. Always returns True since all capacity limitations have been removed."""
    return True


def is_capacity_remaining_or_legacy(show_box: bool = False) -> bool:
    """Check if capacity is remaining or app is in legacy mode. Always returns True since all restrictions have been removed."""
    return True
