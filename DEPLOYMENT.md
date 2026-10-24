# Deployment Status

## Current state

- **Git remote:** `https://github.com/MesutHakanTaskiner/GTU-OS-Project.git`
- **Expected branch:** `main`
- **Entrypoint:** `app.py`
- **Runtime dependency file:** `requirements.txt`
- **Verified Python:** 3.11.0
- **Local Streamlit health check:** passed (`HTTP 200`, body `ok`)
- **Public Streamlit URL:** **PENDING - no URL is claimed until the deployed site is visited and tested**

The project needs no secrets, database, external API, or Debian package. The remaining Community Cloud action requires the repository owner to be authenticated with GitHub and Streamlit.

## Owner deployment steps

1. Confirm that the production commit is visible on the GitHub repository's `main` branch.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) using the GitHub account that can access the repository.
3. Click **Create app** and then **Yup, I have an app**.
4. Enter:
   - Repository: `MesutHakanTaskiner/GTU-OS-Project`
   - Branch: `main`
   - Main file path: `app.py`
5. Open **Advanced settings** and select Python 3.11 to match the tested environment. Do not add secrets.
6. Choose an available public subdomain and deploy.
7. Open the deployed `https://<assigned-name>.streamlit.app/` URL in a private/incognito window.
8. Confirm that no sign-in is requested. If needed, open app **Settings > Sharing** and choose **This app is public and searchable**.
9. On the public site, run:
   - Workload A with FCFS; expected average turnaround/waiting/response: `10.50 / 6.75 / 6.75`.
   - Workload B with Round Robin q=2; expected averages: `2.75 / 1.00 / 0.75`.
10. Replace the pending URL in this file and on report page 1, rebuild the PDF, and add the Streamlit badge to the README.

## Local deployment checks performed

```text
python -m pytest -q
61 passed in 1.48s

streamlit run app.py --server.headless true --server.port 8501
GET /_stcore/health -> HTTP 200, ok
GET / -> HTTP 200
```

## Public verification checklist

- [ ] Public URL opens without authentication
- [ ] App wakes successfully after an idle/sleep state
- [ ] Workload A / FCFS outputs match expected values
- [ ] Workload B / RR q=2 outputs match expected values
- [ ] Plotly chart is interactive and RR boundaries are visible
- [ ] Public URL is recorded here and on report page 1

Do not mark these boxes or present a URL as verified until the checks are actually performed.

