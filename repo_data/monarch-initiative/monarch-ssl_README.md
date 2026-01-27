# monarch-ssl

Manage Monarch Initiative's GCP SSL certificate with this one cool trick

#### Usage

Edit `domains.txt` to match any domains that needed to be added or subracted

Run `./create-cert.sh` to create a new certificate

Check [the certificate console](https://console.cloud.google.com/net-services/loadbalancing/advanced/sslCertificates/list?project=monarch-initiative)
to see if the new cert came up sucessfully.

If it looks good, head to [the load balancer](https://console.cloud.google.com/net-services/loadbalancing/details/http/monarch-balancer?project=monarch-initiative),
hit `Edit` and then navigate to the HTTPS section under frontend and choose the
new certificate in the menu.

<img src='docs/load-balancer-frontend-edit.png' />

Note that these instructions will only work correctly the first time that you
set up the load balancer. For updates to an existing load balancer, you'll
typically already have services behind the load balancer, and swapping out the
certificate with a new one will cause downtime while the new certificate is
being validated. To perform a "rolling deployment" of the new certificate, where
both the old and new one are effective at the same time, see the section below.

### Rolling Certificate Deployment

In order for GCP to validate a certificate, it has to be able to see that it's
been deployed to a resource, e.g. the load balancer. Replacing the existing
certificate with the new one would create a period in which the old certificate
was no longer available, but the new one hadn't yet been validated, causing SSL
errors for anyone trying to connect during that time.

Instead, you can deploy the new certificate alongside the old one, then remove
the old certificate once the new one validates.

After having created your certificate, return to [the load balancer](https://console.cloud.google.com/net-services/loadbalancing/details/http/monarch-balancer?project=monarch-initiative),
hit `Edit` and then navigate to the HTTPS section under frontend.

This time,
click "Additional Certificates" (circled below), which will expand a display of
extra certificates deployed to the load balancer.

<img src='docs/expand-addtl-certs.png' />

Click the "+ Add Certificate" button (circled below), which will add a new blank
row to the list.

<img src='docs/add-new-cert.png' style='border: solid 1px #ddd;' />

In the new row, select the certificate you just created.

Once you verify that the certificate has been validated on the certificate
console, you should be able to safely remove the old certificate. You should
also check that the new certificate you're deploying covers all the domain names
that the load balancer serves before removing it.
