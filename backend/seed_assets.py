from backend.config.database import SessionLocal
from backend.models.asset import Asset


assets = [
    {
        "asset_name": "Ubuntu-Web-Server",
        "asset_type": "SERVER",
        "operating_system": "Ubuntu 24.04 LTS",
        "ip_address": "192.168.56.11",
        "hostname": "ubuntu-web",
        "owner": "Web Team",
        "criticality": "HIGH",
        "environment": "TEST",
    },
    {
        "asset_name": "Windows-Client-Lab",
        "asset_type": "WORKSTATION",
        "operating_system": "Windows 11",
        "ip_address": "192.168.56.12",
        "hostname": "win-client",
        "owner": "IT Team",
        "criticality": "MEDIUM",
        "environment": "TEST",
    },
    {
        "asset_name": "Ubuntu-Database",
        "asset_type": "DATABASE",
        "operating_system": "Ubuntu 22.04 LTS",
        "ip_address": "192.168.56.13",
        "hostname": "ubuntu-db",
        "owner": "Database Team",
        "criticality": "CRITICAL",
        "environment": "TEST",
    },
    {
        "asset_name": "Kali-Pentest-VM",
        "asset_type": "VIRTUAL_MACHINE",
        "operating_system": "Kali Linux",
        "ip_address": "192.168.56.14",
        "hostname": "kali-pentest",
        "owner": "Security Team",
        "criticality": "HIGH",
        "environment": "TEST",
    },
    {
        "asset_name": "Linux-Log-Server",
        "asset_type": "SERVER",
        "operating_system": "Ubuntu 24.04 LTS",
        "ip_address": "192.168.56.15",
        "hostname": "log-server",
        "owner": "SOC Team",
        "criticality": "HIGH",
        "environment": "TEST",
    },
    {
        "asset_name": "Web-App-Test-Server",
        "asset_type": "APPLICATION_SERVER",
        "operating_system": "Ubuntu 22.04 LTS",
        "ip_address": "192.168.56.16",
        "hostname": "web-app-test",
        "owner": "Application Security Team",
        "criticality": "HIGH",
        "environment": "DEVELOPMENT",
    },
    {
        "asset_name": "Network-Monitor",
        "asset_type": "NETWORK_DEVICE",
        "operating_system": "Linux",
        "ip_address": "192.168.56.17",
        "hostname": "network-monitor",
        "owner": "Network Team",
        "criticality": "MEDIUM",
        "environment": "TEST",
    },
    {
        "asset_name": "Security-Analysis-VM",
        "asset_type": "VIRTUAL_MACHINE",
        "operating_system": "Ubuntu 24.04 LTS",
        "ip_address": "192.168.56.18",
        "hostname": "security-analysis",
        "owner": "Security Team",
        "criticality": "HIGH",
        "environment": "DEVELOPMENT",
    },
    {
        "asset_name": "Windows-Server-Lab",
        "asset_type": "SERVER",
        "operating_system": "Windows Server 2022",
        "ip_address": "192.168.56.19",
        "hostname": "win-server",
        "owner": "Infrastructure Team",
        "criticality": "CRITICAL",
        "environment": "TEST",
    },
    {
        "asset_name": "Backup-Server",
        "asset_type": "SERVER",
        "operating_system": "Ubuntu 22.04 LTS",
        "ip_address": "192.168.56.20",
        "hostname": "backup-server",
        "owner": "Infrastructure Team",
        "criticality": "HIGH",
        "environment": "TEST",
    },
]


def seed_assets():

    db = SessionLocal()

    try:

        inserted = 0
        skipped = 0

        for asset_data in assets:

            existing = (
                db.query(Asset)
                .filter(
                    Asset.asset_name
                    == asset_data["asset_name"]
                )
                .first()
            )

            if existing:

                print(
                    f"Skipping existing asset: "
                    f"{asset_data['asset_name']}"
                )

                skipped += 1
                continue

            asset = Asset(
                asset_name=asset_data["asset_name"],
                asset_type=asset_data["asset_type"],
                operating_system=asset_data[
                    "operating_system"
                ],
                ip_address=asset_data["ip_address"],
                hostname=asset_data["hostname"],
                owner=asset_data["owner"],
                criticality=asset_data["criticality"],
                environment=asset_data["environment"],
                status="ACTIVE",
            )

            db.add(asset)
            inserted += 1

        db.commit()

        print()
        print("Asset seeding completed.")
        print(f"Inserted: {inserted}")
        print(f"Skipped:  {skipped}")

    except Exception as error:

        db.rollback()

        print("Asset seeding failed:")
        print(error)

    finally:

        db.close()


if __name__ == "__main__":
    seed_assets()
