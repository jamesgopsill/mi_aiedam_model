from __future__ import annotations

import json
from typing import TYPE_CHECKING, List

from model.broker import broker
from model.clock import clock
from model.job import Job
import model.logics as logics
from model.machine import Machine

from numpy import random


if TYPE_CHECKING:
    from model.typings import JobParams

if __name__ == "__main__":
    rng = random.default_rng(seed=1)

    n = 0

    # Creating the machines
    machines: List[Machine] = []

    for i in range(0, 4):
        m = Machine(id=n, logic=logics.spt, debug=False)
        n += 1
        m.connect()
        machines.append(m)

        m = Machine(id=n, logic=logics.lpt, debug=False)
        n += 1
        m.connect()
        machines.append(m)

    for i in range(0, 12):
        m = Machine(id=n, logic=logics.randomly_select, debug=False)
        n += 1
        m.connect()
        machines.append(m)

    # Creating a demand profile using π as a seed

    jobs: List[Job] = []

    with open("data/pi.txt", "rt") as f:
        pi = f.read()
    pi = pi.replace(".", "")
    pi = [*pi]
    pi = [int(p) for p in pi]
    print(len(pi))

    submission_time = 0
    total_print_time = 0
    for i in range(0, len(pi)):
        submission_time += pi[i] * 20
        if submission_time > 30 * 24 * 60:  # 30 days
            break
        n_jobs = int(pi[i + 1000] * 1.3)
        remainder = submission_time % (24 * 60)
        if remainder > 9 * 60 and remainder < 17 * 60:
            # print(f"Time: {submission_time} adding {n_jobs} jobs")
            for j in range(0, n_jobs):
                pt = int(rng.triangular(48, 240, 600))
                job_params: JobParams = {
                    "id": n,
                    "print_time": pt,
                    "submitted_at": submission_time,
                    "completed_at": -1,
                    "manufactured_by": -1,
                    "selected_at": -1,
                }
                total_print_time += pt
                n += 1
                job = Job(
                    job_params=job_params,
                    debug=False,
                )
                job.connect()
                jobs.append(job)

    print(
        f"Total number of jobs: {len(jobs)}. Total print time: {total_print_time}"
    )

    # Runtime (in mins)
    # Note. no shuffling of machines or jobs.
    for i in range(0, 30 * 24 * 60):
        for m in machines:
            m.next()
        for j in jobs:
            j.next()
        broker.next()
        clock.tick()

    # Write out the results
    with open("out/best_case_broker.json", "wt") as f:
        details = {
            "messages_sent": broker.messages_sent,
            "messages_received": broker.messages_received,
        }
        f.write(json.dumps(details))

    machines.sort(key=lambda x: x.id)
    with open("out/best_case_machines.json", "wt") as f:
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
    with open("out/best_case_jobs.json", "wt") as f:
        f.write("[\n")
        for i, j in enumerate(jobs):
            if i != len(jobs) - 1:
                f.write(json.dumps(j.job_params) + ",\n")
            else:
                f.write(json.dumps(j.job_params) + "\n]")
