import argparse
import sxccd
import h5py
import time
import numpy as np

def takeImage( exp_ms, delay=0, prefix="images", nExp = 1, singleImage=True, bin=1 ):

    sx = sxccd.Camera()
    sx.model()
    sx.reset()

    params = sx.parameters()
    width = params["width"]
    height = params["height"]
    w = int( width / bin )
    h = int( height / bin )

    filename = prefix + "_" + str(exp_ms).zfill(6) + ".h5"
    f = h5py.File(filename, 'w')
    avg_set = f.create_dataset("avg", (h, w), dtype=np.float32)
    if singleImage:
        img_set = f.create_dataset("imgs", (h, w, nExp),
                                    chunks=(h, w, 1), dtype="uint32")

    img_avg = np.zeros( (h,w), dtype=np.uint32)

    if delay>0:
        print("=========== camera exposure starts in "
                + str(delay) + " sec "
                + "===========" )
        time.sleep(delay)

    for t in range(nExp):
        t1 = time.time()
        img = sx.readPixelsDelayed( exp_ms, width, height, x_bin=bin, y_bin=bin,
                                x_offset=0, y_offset=0, verbose=False)
        img_avg += img

        if singleImage:
            img_set[:,:,t] = img

        t2 = time.time()
        print("image " + str(t+1) + " done in " + str(t2-t1) + " sec \a")

    img_avg = img_avg.astype(np.float32) / nExp
    avg_set[:] = img_avg

    print("========== done " + str(nExp) + " images ========== \a\a\a")

    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('exp', type=int,# dest="exp",
                        default=1,
                        help="Exposure time in ms")
    parser.add_argument('--delay', "-d", type=int, dest="delay",
                        default=0,
                        help="Delay before exposure starts in sec")
    parser.add_argument('--prefix', "-o", type=str, dest='prefix',
                        default="images",
                        help="Prefix of output filename")
    parser.add_argument('--number', "-n", type=int, dest="num",
                        default=1,
                        help="Number of exposures to be performed")
    parser.add_argument('--bin', "-b", type=int, dest="bin",
                        default=1,
                        help="Number of pixels to bin")
    parser.add_argument('--single-image', "-s", dest="single",
                        action="store_true",
                        help="Whether to save every single image or just the average")

    args = parser.parse_args()
    print(args)
    takeImage( exp_ms=args.exp, delay=args.delay, prefix=args.prefix,
                nExp = args.num, singleImage=args.single, bin=args.bin )
