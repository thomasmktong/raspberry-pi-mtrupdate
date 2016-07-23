from sense_hat import SenseHat
import threading
import time

class Screen:

    sense = SenseHat()

    # Color constants
    color_line_east = [83, 183, 232]
    color_line_kwuntong = [0, 171, 78]
    color_line_tsuenwan = [237, 29, 36]
    color_line_island = [0, 125, 197]
    color_line_tungchung = [247, 148, 62]
    color_line_airport = [0, 136, 138]
    color_line_tseungkwano = [125, 73, 157]
    color_line_west = [163, 35, 143]
    color_line_maonshan = [146, 48, 17]
    color_line_disney = [241, 115, 172]

    # Get color of line, return white if not specified
    def color_of_line(self, line):
        return {
            'isline': self.color_line_island,
            'ktline': self.color_line_kwuntong,
            'twline': self.color_line_tsuenwan,
            'tkline': self.color_line_tseungkwano,
            'tcline': self.color_line_tungchung,
            'erline': self.color_line_east,
            'moline': self.color_line_maonshan,
            'wrline': self.color_line_west,
            'aeline': self.color_line_airport,
            'disney': self.color_line_disney
        }.get(line, [255, 255, 255])


    # Pixel constants
    ce = color_empty = [0, 0, 0]
    cl = color_load = [0, 0, 255]
    cg = color_good = [0, 255, 0]
    cf = color_fail = [255, 0, 0]

    image_load = [
        ce, ce, ce, ce, ce, ce, ce, ce,
        ce, cl, cl, cl, cl, cl, cl, ce,
        ce, ce, ce, ce, ce, ce, cl, ce,
        ce, cl, ce, ce, ce, cl, cl, cl,
        cl, cl, cl, ce, ce, ce, cl, ce,
        ce, cl, ce, ce, ce, ce, ce, ce,
        ce, cl, cl, cl, cl, cl, cl, ce,
        ce, ce, ce, ce, ce, ce, ce, ce,
    ]

    image_tick = [
        ce, ce, ce, ce, ce, ce, ce, cg,
        ce, ce, ce, ce, ce, ce, cg, ce,
        ce, ce, ce, ce, ce, cg, ce, ce,
        cg, ce, ce, ce, cg, ce, ce, ce,
        ce, cg, ce, cg, ce, ce, ce, ce,
        ce, ce, cg, ce, ce, ce, ce, ce,
        ce, ce, ce, ce, ce, ce, ce, ce,
        ce, ce, ce, ce, ce, ce, ce, ce
    ]

    image_cross = [
        cf, ce, ce, ce, ce, ce, ce, cf,
        ce, cf, cf, ce, ce, cf, cf, ce,
        ce, ce, ce, cf, cf, ce, ce, ce,
        ce, ce, ce, cf, cf, ce, ce, ce,
        ce, cf, cf, ce, ce, cf, cf, ce,
        cf, ce, ce, ce, ce, ce, ce, cf,
        ce, ce, ce, ce, ce, ce, ce, ce,
        ce, ce, ce, ce, ce, ce, ce, ce
    ]

    # Get image from status tuple (refer status.py)
    # the image will have a big tick / cross on top
    # with line color dots at the bottom
    def image_of_status(self, status):
        image = []

        # copy image arrays above as template
        if(status[0]):
            image = list(self.image_tick)
        else:
            image = list(self.image_cross)

        # add line color dots at the bottom
        # convert data type from set to list
        lines = list(status[1])

        for i, line in enumerate(lines):
            line_color = self.color_of_line(line)
            image[len(image) - 1 - i] = line_color

        return image


    # runtime variables
    lock = threading.RLock()
    loading = True
    controlling = False

    def display_status(self, status):
        with self.lock:
            self.loading = False
            if(not self.controlling):
                self.sense.set_pixels(self.image_of_status(status))

                # if good, the image should clear after idle
                # if fail, display cross until fixed
                if(status[0]):
                    self.display_idle_clear()

    def display_loading(self):
        with self.lock:
            self.loading = True
            self.controlling = False
            self.sense.set_pixels(self.image_load)

        i = 1
        while True:
            time.sleep(0.5)
            with self.lock:
                if(not self.loading):
                    break
                self.sense.set_rotation(90 * (i % 2))
                i += 1

    def display_loading_async(self):
        self.thread = threading.Thread(target=self.display_loading)
        self.thread.start()


    def display_idle_clear(self):
        time.sleep(10)
        with self.lock:
            if(not self.loading and not self.controlling):
                self.display_clear()


    def display_clear(self):
        self.sense.clear()


    def display_rotate(self, degree):
        if(not self.loading):
            self.sense.set_rotation(degree)


# when this file executed individually, run test
if(__name__ == "__main__"):

    screen = Screen()
    screen.display_loading_async()
    time.sleep(2.5)

    status = (True, set(['twline', 'isline', 'erline']))
    screen.display_status(status)
