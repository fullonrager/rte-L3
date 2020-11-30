from __future__ import unicode_literals

from .fragment import FragmentFD
from ..compat import compat_urllib_error
from ..utils import (
    DownloadError,
    urljoin,
)

import subprocess
import shutil
import io
import os
import sys

temp_dir = os.path.join(os.path.dirname(__file__), "../../temp/")


class DashSegmentsFD(FragmentFD):
    """
    Download segments in a DASH manifest
    """

    FD_NAME = 'dashsegments'

    def real_download(self, filename, info_dict):
        fragment_base_url = info_dict.get('fragment_base_url')
        fragments = info_dict['fragments'][:1] if self.params.get(
            'test', False) else info_dict['fragments']

        ctx = {
            'filename': filename,
            'total_frags': len(fragments),
        }

        self._prepare_and_start_frag_download(ctx)

        fragment_retries = self.params.get('fragment_retries', 0)
        skip_unavailable_fragments = self.params.get('skip_unavailable_fragments', True)

        frag_index = 0
        fragment_urls = []
        fragment_names = []
        for i, fragment in enumerate(fragments):
            frag_index += 1
            # In DASH, the first segment contains necessary headers to
            # generate a valid MP4 file, so always abort for the first segment
            fatal = i == 0 or not skip_unavailable_fragments
            fragment_url = fragment.get('url')
            if not fragment_url:
                assert fragment_base_url
                fragment_url = urljoin(fragment_base_url, fragment['path'])
            #success, frag_content = self._download_fragment(ctx, fragment_url, info_dict)
            #if not success:
            #    return False
            #self._append_fragment(ctx, frag_content)
            base_name = os.path.basename(filename)
            
            fragment_names.append('{}_fragment_{:d}.m4s'.format(base_name, frag_index))
            fragment_urls.append('{}\n\tout={}_fragment_{:d}.m4s'.format(fragment_url, base_name, frag_index))

        fragment_data = {
            'urls': fragment_urls,
            'names': fragment_names
        }

        txt_file = os.path.join(temp_dir, os.path.basename(ctx['tmpfilename']) + "_urls.txt")
        
        with open(txt_file, "w") as txt:
            txt.write('\n'.join(fragment_data['urls']))

        cmd = [os.path.join(os.path.dirname(__file__), '../../binaries/aria2c'), '-i', txt_file, '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36']
        cmd += ['--allow-overwrite=true', '--auto-file-renaming=false', '--file-allocation=none', '--summary-interval=0', '--retry-wait=5', '--max-file-not-found=5']
        cmd += ['--uri-selector=inorder', '--console-log-level=warn', '--download-result=hide', '-x16', '-j16', '-s16', '--dir', temp_dir]

        aria_out = subprocess.run(cmd)
        aria_out.check_returncode

        with open(ctx['tmpfilename'], 'wb') as dest:
            for i in fragment_data['names']:
                shutil.copyfileobj(open(os.path.join(temp_dir, i), 'rb'), dest)

        for x in fragment_data['names']:
            try:
                file_path = os.path.join(temp_dir, x)
                os.remove(file_path)
            except OSError as e:
                print("Error: %s : %s" % (file_path, e.strerror))
                    
        self._finish_frag_download(ctx)
        
        return True
                # except compat_urllib_error.HTTPError as err:
                #     # YouTube may often return 404 HTTP error for a fragment causing the
                #     # whole download to fail. However if the same fragment is immediately
                #     # retried with the same request data this usually succeeds (1-2 attemps
                #     # is usually enough) thus allowing to download the whole file successfully.
                #     # To be future-proof we will retry all fragments that fail with any
                #     # HTTP error.
                #     count += 1
                #     if count <= fragment_retries:
                #         self.report_retry_fragment(err, frag_index, count, fragment_retries)
                # except DownloadError:
                #     # Don't retry fragment if error occurred during HTTP downloading
                #     # itself since it has own retry settings
                #     if not fatal:
                #         self.report_skip_fragment(frag_index)
                #         break
                #     raise

            # if count > fragment_retries:
            #     if not fatal:
            #         self.report_skip_fragment(frag_index)
            #         continue
            #     self.report_error('giving up after %s fragment retries' % fragment_retries)
            #     return False


        # return True
