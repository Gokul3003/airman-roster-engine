class CapacityManager:

    def __init__(self):
        self.sim_bookings = set()

    def register_existing_allocations(self, roster):

        if roster is None or "roster" not in roster:
            return

        for day_block in roster["roster"]:
            for slot in day_block.get("slots", []):
                if slot.get("activity") == "SIM":
                    self.sim_bookings.add(
                        (slot["date"], slot["slot_id"])
                    )

    def register_sim(self, date, slot_id):
        self.sim_bookings.add((date, slot_id))