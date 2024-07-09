from src.ucs_alg_node.cli import MinioCli

host = '62.234.16.239'
port = 9090
bucket = 'ucs-alg'
fname = 'vid_tmp.mp4'

cli = MinioCli(host, port, bucket, 'admin', 'admin1234')

#
# ret = cli.upload(fname, './vid_tmp.mp4')
# if ret == 0:
#     print('file uploaded')
# else:
#     print('file upload failed')
#
# ret = cli.download(fname, './vid_tmp_minio.mp4')
# if ret == 0:
#     print('file downloaded')
# else:
#     print('file download failed')

# flist = cli.query_all()
# flist = [f for f in flist]
# print(flist)

f = cli.query(fname)
if f:
    a = cli.fetch_share_url(fname)
    print(a)
    cnt = cli.count()
    print('%d files in bucket' % cnt)
