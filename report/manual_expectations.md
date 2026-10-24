# Independent Manual Scheduling Notes

These expected results were derived from the policy rules before running the implementation. Intervals are half-open.

## Workload A

Input: P1=(0,8), P2=(1,4), P3=(2,2), P4=(4,1).

- FCFS: `P1[0,8) P2[8,12) P3[12,14) P4[14,15)`. Metrics `(C,T,W,R)`: P1=(8,8,0,0), P2=(12,11,7,7), P3=(14,12,10,10), P4=(15,11,10,10). Averages: T=10.50, W=6.75, R=6.75.
- SJF: `P1[0,8) P4[8,9) P3[9,11) P2[11,15)`. Metrics: P1=(8,8,0,0), P2=(15,14,10,10), P3=(11,9,7,7), P4=(9,5,4,4). Averages: T=9.00, W=5.25, R=5.25.
- SRTF: `P1[0,1) P2[1,2) P3[2,4) P4[4,5) P2[5,8) P1[8,15)`. Metrics: P1=(15,15,7,0), P2=(8,7,3,0), P3=(4,2,0,0), P4=(5,1,0,0). Averages: T=6.25, W=2.50, R=0.00.
- RR q=2: `P1[0,2) P2[2,4) P3[4,6) P1[6,8) P4[8,9) P2[9,11) P1[11,13) P1[13,15)`. Metrics: P1=(15,15,7,0), P2=(11,10,6,1), P3=(6,4,2,2), P4=(9,5,4,4). Averages: T=8.50, W=4.75, R=1.75.

## Workload B

Input: P1=(2,3), P2=(2,1), P3=(8,2), P4=(9,1).

- FCFS: `IDLE[0,2) P1[2,5) P2[5,6) IDLE[6,8) P3[8,10) P4[10,11)`. Metrics: P1=(5,3,0,0), P2=(6,4,3,3), P3=(10,2,0,0), P4=(11,2,1,1). Averages: T=2.75, W=1.00, R=1.00.
- SJF: `IDLE[0,2) P2[2,3) P1[3,6) IDLE[6,8) P3[8,10) P4[10,11)`. Metrics: P1=(6,4,1,1), P2=(3,1,0,0), P3=(10,2,0,0), P4=(11,2,1,1). Averages: T=2.25, W=0.50, R=0.50.
- SRTF: same merged timeline and metrics as SJF. At t=9, P3 and P4 both have one unit remaining, so P3 keeps the CPU.
- RR q=2: `IDLE[0,2) P1[2,4) P2[4,5) P1[5,6) IDLE[6,8) P3[8,10) P4[10,11)`. Metrics: P1=(6,4,1,0), P2=(5,3,2,2), P3=(10,2,0,0), P4=(11,2,1,1). Averages: T=2.75, W=1.00, R=0.75.

## Targeted oracle cases

- Idle gaps, FCFS: `IDLE[0,2) I1[2,4) IDLE[4,6) I2[6,7)`; both processes have zero waiting and response.
- Simultaneous tie, SJF: `T2[0,1) T3[1,2) T1[2,5)`; input order resolves the equal one-unit bursts.
- SRTF strict/equal case: `E1[0,2) E3[2,3) E1[3,6) E2[6,10)`. E2 does not preempt E1 at t=1 because both have four units remaining; E3 does preempt at t=2 because one is strictly shorter than E1's three.
- RR boundary case with B1=(0,4), B2=(2,1), q=2: `B1[0,2) B2[2,3) B1[3,5)`. The arrival at the exact boundary enters before B1 is re-enqueued.

