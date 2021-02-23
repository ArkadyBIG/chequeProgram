import cv2
import numpy as np


def points_distance(p1, p2):
    return int(np.linalg.norm([p1[0]-p2[0], p1[1]-p2[1]]))


def crop(image, points, need_sort):
    inter = np.float32(points)

    width = points_distance(inter[0], inter[1])
    height = points_distance(inter[0], inter[2])
    size = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv2.getPerspectiveTransform(inter, size)

    return cv2.warpPerspective(image, matrix, (width, height))


def get_extreme_points(points) -> np.array:
    assert len(points) == 4, 'only for 4 points!!!'
    points = np.array(points)

    points = np.squeeze(points)
    ordered_by_y_coord = sorted(points, key=lambda _point: _point[1])

    # find list of distances which contains longest distance(length of big diagonal)
    top1, top2 = ordered_by_y_coord[0], ordered_by_y_coord[1]
    distances1 = [np.linalg.norm(top1 - _point) for _point in points]
    distances2 = [np.linalg.norm(top2 - _point) for _point in points]
    distances = (distances1, distances2)[float(max(distances1)) < float(max(distances2))]

    # order by distance
    ordered_points = [points[index] for _, index in sorted(zip(distances, range(points.shape[0])))]

    # switch because longer goes second then shorter then diagonal distance
    ordered_points[1], ordered_points[2] = ordered_points[2], ordered_points[1]

    if ordered_points[0][0] > ordered_points[1][0]:
        # check if reverse
        ordered_points[0], ordered_points[1] = ordered_points[1], ordered_points[0]
        ordered_points[2], ordered_points[3] = ordered_points[3], ordered_points[2]

    return np.array(ordered_points)


def main():
    import itertools

    def pass_f(*args, **kwargs): return

    tracked_window = 'TrackedBars'
    cv2.namedWindow(tracked_window)
    for point, axis in itertools.product(range(4), range(2)):
        cv2.createTrackbar(f'{point+1}{axis}', tracked_window, 0, 500, pass_f)

    while True:
        background = np.zeros((700, 700), dtype='uint8')
        points = [tuple((100+cv2.getTrackbarPos(i+j, tracked_window) for j in '01')) for i in '1234']
        points = get_extreme_points(points)
        for i in range(4):
            cv2.ellipse(background, tuple(points[i]), (10, 10), 0, 0, 360, 80, thickness=10)
            cv2.putText(background, f'{i + 1}', tuple(points[i]), cv2.FONT_HERSHEY_SIMPLEX, 1.5, thickness=5, color=200)

        cv2.imshow(tracked_window, background)

        if cv2.waitKey(2) == 27:
            break
        if not cv2.getWindowProperty(tracked_window, cv2.WND_PROP_VISIBLE):
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
