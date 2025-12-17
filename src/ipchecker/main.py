import time
import smtplib
import urllib.request
import urllib.error
import socket
import os
from email.mime.text import MIMEText
import CloudFlare

SCAN_INTERVAL_MIN = os.getenv("SCAN_INTERVAL_MIN")
DOMAIN = os.getenv("DOMAIN")
CLOUDFLARE_TOKEN = os.getenv("CLOUDFLARE_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_EMAIL_PASSWORD = os.getenv("SENDER_EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def avail_internet(host="http://google.com"):
    try:
        urllib.request.urlopen(host)  # Python 3.x
        return True
    except:
        return False


def get_dns_ip():
    print("\tConnecting to Cloudflare..")
    cf = CloudFlare.CloudFlare(token=CLOUDFLARE_TOKEN)

    print("\tGetting domain zone...")
    zone_id = cf.zones.get(params={"name": DOMAIN})[0]["id"]

    print("\tGetting A record...")
    a_record = cf.zones.dns_records.get(
        zone_id, params={"name": DOMAIN, "type": "A"}
    )[0]

    print("\t" + a_record["content"])
    return a_record["content"]


def get_public_ip():
    sites = [
        "https://jsonip.com/",
        "https://ipaddr.me/",
        "https://api.ipify.org/",
    ]
    print("Getting public ip...")
    public_ip = None
    for url in sites:
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                public_ip = response.read().decode("utf-8").strip()
        except (urllib.error.URLError, socket.timeout) as e:
            print(f"Skipping {url}: {e}")
            continue
    return public_ip


def update_cloud_flare(dns_ip, public_ip):
    if dns_ip and public_ip:
        print("\tConnecting to Cloudflare..")
        cf = CloudFlare.CloudFlare(token=CLOUDFLARE_TOKEN)

        print("\tGetting domain zone...")
        zone_id = cf.zones.get(params={"name": DOMAIN})[0]["id"]

        print("\tGetting A record...")
        a_record = cf.zones.dns_records.get(
            zone_id, params={"name": DOMAIN, "type": "A"}
        )[0]

        if a_record["content"] != public_ip:
            print(
                "\tUpdating A record from ({}) to ({})".format(
                    a_record["content"], public_ip
                )
            )
            old_ip = a_record["content"]
            a_record["content"] = public_ip

            cf.zones.dns_records.put(zone_id, a_record["id"], data=a_record)
            send_email_notification(
                body="Cloudflare DNS IP Updated from {} to new IP: {} !".format(
                    old_ip, public_ip
                )
            )
        else:
            print(
                "\tCloudflare IP is already the same as the current one! Not changing anything."
            )
        print("\tDone")


def send_email_notification(
    body="Public IP changed",
    subject="IP_CHECKER",
    sender=SENDER_EMAIL,
    recipients=[RECIPIENT_EMAIL],
    password=SENDER_EMAIL_PASSWORD,
):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()
    print("\tEmail Sent!")


def main():
    time.sleep(5)

    # print(SCAN_INTERVAL_MIN)
    # print(DOMAIN)
    # print(CLOUDFLARE_TOKEN)
    # print(SENDER_EMAIL)
    # print(SENDER_EMAIL_PASSWORD)
    # print(RECIPIENT_EMAIL)

    if (
        SCAN_INTERVAL_MIN
        and DOMAIN
        and CLOUDFLARE_TOKEN
        and SENDER_EMAIL
        and SENDER_EMAIL_PASSWORD
        and RECIPIENT_EMAIL
    ):
        _INTERVAL = int(SCAN_INTERVAL_MIN) * 60

        was_error = False
        while True:
            if avail_internet():
                try:
                    PUBLIC_IP = get_public_ip()
                    if not PUBLIC_IP:
                        print("Couldn't retrieve public ip!")
                        send_email_notification(
                            body="IPCHECKER COULDNT GET PUBLIC IP !"
                        )
                    DNS_IP = get_dns_ip()

                    if was_error:
                        send_email_notification(body="IPCHECKER RUNNING FINE!")
                        was_error = False

                    print(
                        "Current PUBLIC_IP: {} DNS_IP: {}".format(
                            PUBLIC_IP, DNS_IP
                        )
                    )
                    if PUBLIC_IP != DNS_IP:
                        update_cloud_flare(DNS_IP, PUBLIC_IP)
                except Exception as e:
                    print("=" * 10)
                    print(e)
                    send_email_notification(body="ERROR: \n{}".format(e))
                    was_error = True
                    print("=" * 10)
            else:
                print("<No internet access, skipping ip address DNS update!>")

            time.sleep(_INTERVAL)
    else:
        print("Environment not set!")


if __name__ == "__main__":
    main()
