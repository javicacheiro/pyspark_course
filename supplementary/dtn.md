# DTN
## How to upload data
Depending on the size of the data that you want to upload you have different options:

- For small amounts of data (`<10GB`) you can use scp directly.
- For large amounts of data it is recommended that you use the GridFTP service through Globus Online.

In all cases it is recommended that you do the transfer against our DTN server: dtn.srv.cesga.es, this will give you a much better network performance. In Globus Online the endpoint of this server is: `cesga#dtn`.

## Using the DTN
- [CESGA DTN User Guide: Globus](http://bigdata.cesga.es/dtn-user-guide/globus.html)

NOTE: You have to do a request to open access from your IP address or the DTN repository.

Example:
- Transfer one of the cosmoDC2 images from the `Duke Cosmology Public` to `cesga#dtn` (to LUSTRE).

## Running tests to ESnet Data Transfer Nodes (DTNs)
ESnet has deployed a set of test hosts for high-speed disk-to-disk testing. Anyone on an R&E network anywhere in the world can use these hosts for anonymous GridFTP access. These hosts are capable saturating a 10+Gbps network reading from disk. These hosts are an example of a "Data Transfer Node", or DTN, for use in a Science DMZ.
- [ESnet Data Transfer Nodes](https://fasterdata.es.net/performance-testing/DTNs/)

Each host has a high-performance disk array, mounted as /data1. The following test files are available on each server, and are generated using "/dev/urandom" (the size is what you would expect from reading the filename):

```
/data1/1M.dat, /data1/10M.dat, /data1/50M.dat, /data1/100M.dat,
/data1/1G.dat, /data1/10G.dat, /data1/50G.dat, /data1/100G.dat, /data1/500G.dat
```

To test data transfers we can use:
- ESnet CERN read-only
- ESnet Starlight DTN (Anonymous read only testing)
