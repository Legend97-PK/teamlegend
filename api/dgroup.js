const http = require("http");
const https = require("https");
const zlib = require("zlib");

module.exports = async (req, res) => {
  const get = (url, headers) =>
    new Promise((resolve, reject) => {
      const lib = url.startsWith("https") ? https : http;
      const request = lib.get(url, { headers }, (response) => {
        let chunks = [];

        response.on("data", (chunk) => chunks.push(chunk));
        response.on("end", () => {
          const buffer = Buffer.concat(chunks);

          
          const encoding = response.headers["content-encoding"];
          try {
            if (encoding === "gzip") {
              zlib.gunzip(buffer, (err, decoded) => {
                if (err) return reject(err);
                resolve(decoded.toString());
              });
            } else if (encoding === "deflate") {
              zlib.inflate(buffer, (err, decoded) => {
                if (err) return reject(err);
                resolve(decoded.toString());
              });
            } else {
              resolve(buffer.toString());
            }
          } catch (e) {
            reject(e);
          }
        });
      });

      request.on("error", reject);
    });

  const { type } = Object.fromEntries(
    new URL(req.url, "http://localhost").searchParams
  );

  if (!type) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: "Missing ?type parameter" }));
  }

  const headers = {
    "User-Agent":
      "Mozilla/5.0 (Linux; Android 15; 23106RN0DA Build/AP3A.240905.015.A2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.34 Mobile Safari/537.36",
    Accept: "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    Cookie: "PHPSESSID=rql5lghtfkaeht7l39haolcaoc",
  };

  let url;

  if (type === "numbers") {
    url =
      "http://139.99.63.204/ints/client/res/data_smsnumbers.php?frange=&fclient=&sEcho=2&iColumns=6&sColumns=%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=-1&mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&_=1766032327885";
    headers.Referer =
      "http://139.99.63.204/ints/client/MySMSNumbers";
  } else if (type === "sms") {
    url =
      "http://139.99.63.204/ints/client/res/data_smscdr.php?fdate1=2025-12-18%2000:00:00&fdate2=2125-12-18%2023:59:59&frange=&fnum=&fcli=&fgdate=&fgmonth=&fgrange=&fgnumber=&fgcli=&fg=0&sEcho=2&iColumns=7&sColumns=%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=-1&mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1&_=1766032579586";
    headers.Referer =
      "http://139.99.63.204/ints/client/SMSCDRStats";
  } else {
    res.statusCode = 400;
    return res.end(
      JSON.stringify({ error: "Invalid type (use sms or numbers)" })
    );
  }

  try {
    const data = await get(url, headers);
    res.setHeader("Content-Type", "application/json");
    res.end(data);
  } catch (err) {
    res.statusCode = 500;
    res.end(JSON.stringify({ error: "Fetch failed", details: err.message }));
  }
};
