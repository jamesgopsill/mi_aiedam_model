from __future__ import annotations

import json
from typing import TYPE_CHECKING, List

from model.broker import broker
from model.clock import clock
from model.job import Job
from model.logics import randomly_select
from model.machine import Machine

from numpy import random

if TYPE_CHECKING:
    from model.typings import JobParams

if __name__ == "__main__":
    rng = random.default_rng(seed=1)

    n = 0

    # Creating the machines
    machines: List[Machine] = []
    machine_one = Machine(id=n, logic=randomly_select, debug=True)
    n += 1
    machine_one.connect()
    machines.append(machine_one)

    machine_two = Machine(id=n, logic=randomly_select, debug=True)
    n += 1
    machine_two.connect()
    machines.append(machine_two)

    # Creating the jobs
    jobs: List[Job] = []

    for i in range(0, 10):
        job_params: JobParams = {
            "id": n,
            "print_time": 10,
            "submitted_at": int(rng.integers(0, 24 * 60)),
            "completed_at": -1,
            "manufactured_by": -1,
            "selected_at": -1,
        }
        n += 1
        job = Job(
            job_params=job_params,
            debug=True,
        )
        job.connect()
        jobs.append(job)

    # Runtime (in mins)
    # Note. no shuffling of machines or jobs.
    for i in range(0, 24 * 60):
        for m in machines:
            m.next()
        for j in jobs:
            j.next()
        broker.next()
        clock.tick()

    # Write out the results
    with open("out/broker.json", "wt") as f:
        details = {
            "messages_sent": broker.messages_sent,
            "messages_received": broker.messages_received,
        }
        f.write(json.dumps(details))

    machines.sort(key=lambda x: x.id)
    with open("out/machines.json", "wt") as f:
        f.write("[\n")
        for i, m in enumerate(machines):
            details = {
                "machine_id": m.id,
                "jobs_brokered": m.jobs_brokered,
                "rejections": m.rejections,
                "messages_received": m.messages_received,
                "messages_sent": m.messages_sent,
            }

            if i != len(machines) - 1:
                f.write(json.dumps(details) + ",\n")
            else:
                f.write(json.dumps(details) + "\n]")

    jobs.sort(key=lambda x: x.id)
    with open("out/jobs.json", "wt") as f:
        f.write("[\n")
        for i, j in enumerate(jobs):
            if i != len(jobs) - 1:
                f.write(json.dumps(j.job_params) + ",\n")
            else:
                f.write(json.dumps(j.job_params) + "\n]")
