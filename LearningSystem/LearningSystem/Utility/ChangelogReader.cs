using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace LearningSystem.Utility
{
    internal class ChangelogReader
    {
        public string Changelog(string raw)
        {
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(raw);

            // execute the request
            HttpWebResponse response = (HttpWebResponse)
                request.GetResponse();
            // we will read data via the response stream
            StringBuilder sb = new StringBuilder();
            Stream resStream = response.GetResponseStream();
            byte[] buf = new byte[1024];
            int count;
            do
            {
                // fill the buffer with data
                count = resStream.Read(buf, 0, buf.Length);

                // make sure we read some data
                if (count != 0)
                {
                    // translate from bytes to ASCII text
                    string? tempString = System.Text.Encoding.ASCII.GetString(buf, 0, count);

                    // continue building the string
                    sb.Append(tempString);
                }
            }
            while (count > 0); // any more data to read?

            // print out page source
            return sb.ToString();
        }
    }
}
