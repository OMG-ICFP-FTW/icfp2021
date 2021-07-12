#include <string>
#include <memory>
#include <vector>
#include <unordered_set>
#include <cmath>
#include <string>
#include <fstream>
#include <streambuf>
#include <iostream>
#include <thread>
#include <stdexcept>
#include <sstream>

#include <stdint.h>
#include <stdlib.h>
#include <time.h>

#include <SDL.h>
#include <curl/curl.h>

#include "json.h"

using json = nlohmann::json;

template<typename ... Args>
std::string string_format( const std::string& format, Args ... args )
{
  int size_s = std::snprintf( nullptr, 0, format.c_str(), args ... ) + 1; // Extra space for '\0'
  if( size_s <= 0 ){ throw std::runtime_error( "Error during formatting." ); }
  auto size = static_cast<size_t>( size_s );
  auto buf = std::make_unique<char[]>( size );
  std::snprintf( buf.get(), size, format.c_str(), args ... );
  return std::string( buf.get(), buf.get() + size - 1 ); // We don't want the '\0' inside
}

std::vector<std::string> string_split(std::string s, std::string delimiter) {
  size_t pos_start = 0, pos_end, delim_len = delimiter.length();
  std::string token;
  std::vector<std::string> res;

  while ((pos_end = s.find (delimiter, pos_start)) != std::string::npos) {
    token = s.substr(pos_start, pos_end - pos_start);
    pos_start = pos_end + delim_len;
    res.push_back(token);
  }

  res.push_back(s.substr(pos_start));
  return res;
}

std::vector<int> parse_csv(const std::string &s) {
  char delim = ',';
  std::vector<int> result;
  std::stringstream ss(s);
  std::string item;

  while (getline(ss, item, delim)) {
    result.push_back(atoi(item.c_str()));
  }

  return result;
}

size_t writeFunction(void *ptr, size_t size, size_t nmemb, std::string* data) {
    data->append((char*) ptr, size * nmemb);
    return size * nmemb;
}

std::string GetProblem(int problem_id) {
  std::string response_string;
  auto curl = curl_easy_init();
  if (curl) {
    auto get_url = string_format("https://poses.live/api/problems/%d", problem_id);
    curl_easy_setopt(curl, CURLOPT_URL, get_url.c_str());

    auto auth_header = string_format("Authorization: Bearer %s", std::getenv("STEEZYKEY"));
    struct curl_slist* headers = NULL;
    headers = curl_slist_append(headers, auth_header.c_str());
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    std::string header_string;
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeFunction);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, &header_string);

    char* url;
    long response_code;
    double elapsed;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
    curl_easy_getinfo(curl, CURLINFO_TOTAL_TIME, &elapsed);
    curl_easy_getinfo(curl, CURLINFO_EFFECTIVE_URL, &url);

    curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    curl = NULL;
  }
  return response_string;
}

std::string SubmitProblem(int problem_id, const std::string& data) {
  std::string response_string;
  auto curl = curl_easy_init();
  if (curl) {
    auto get_url = string_format("https://poses.live/api/problems/%d/solutions", problem_id);
    curl_easy_setopt(curl, CURLOPT_URL, get_url.c_str());

    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());

    auto auth_header = string_format("Authorization: Bearer %s", std::getenv("STEEZYKEY"));
    struct curl_slist* headers = NULL;
    headers = curl_slist_append(headers, auth_header.c_str());
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    std::string header_string;
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeFunction);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, &header_string);

    char* url;
    long response_code;
    double elapsed;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
    curl_easy_getinfo(curl, CURLINFO_TOTAL_TIME, &elapsed);
    curl_easy_getinfo(curl, CURLINFO_EFFECTIVE_URL, &url);

    curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    curl = NULL;
  }
  return response_string;
}
struct Point {
  int16_t x;
  int16_t y;

  bool operator==(const Point& p) const {
    return (x == p.x) && (y == p.y);
  }
};

struct PointHash {
  std::size_t operator()(const Point& p) const {
    // Modified Bernstein hash
    // http://eternallyconfuzzled.com/tuts/algorithms/jsw_tut_hashing.aspx
    return (33UL * p.x)^p.y;
  }
};

struct Vec {
  float x;
  float y;

  Point quantize() const {
    float rx = std::lroundf(x);
    float ry = std::lroundf(y);
    return {static_cast<int16_t>(rx), static_cast<int16_t>(ry)};
  }

  Vec norm() const {
    const float m = mag();
    if (m == 0.0f) {
      return {0.0f, 0.0f};
    }
    return {x/m, y/m};
  }

  float mag() const {
    const float m = std::sqrt(x*x + y*y);
    return m;
  }

  Vec cronch() const {
    float m = std::sqrt(mag());
    const Vec dir = norm();
    return {m*dir.x, m*dir.y};;
  }
};

struct Force {
  Vec net;
  float total;
};

using Points = std::vector<Point>;

struct Edge {
  uint32_t s;
  uint32_t e;
};

struct Solution {
  uint32_t dislikes;
  Points assigned;
};

struct Connection {
  uint32_t other;
  float distance;
};

struct Problem {
  Points verts;
  Points hole;

  std::vector<Edge> edges;
  std::vector<float> original_distances;

  uint32_t epsilon;
  float ep;

  // List of all points that lie within the hole.
  Points points_in_hole;
  std::unordered_set<Point, PointHash> valid_points;

  // For each vert, a list of vert IDs that it is connected to, and the original
  // distances.
  std::vector<std::vector<Connection>> connections;

  // The centroid of the cloud of points in the hole.
  Point center;

  // The min and max points of the bounding box of the hole
  Point min;
  Point max;
};

struct Distance {
  uint32_t distance;
  Point p;
};

uint32_t sqd(const Point& p1, const Point& p2) {
  const int dx = p1.x - p2.x;
  const int dy = p1.y - p2.y;
  return dx*dx + dy*dy;
}

float sqd(const Vec& v1, const Vec& v2) {
  const float dx = v1.x - v2.x;
  const float dy = v1.y - v2.y;
  return dx*dx + dy*dy;
}

struct DistanceMap {
  struct Range {
    const Distance* start;
    size_t size;
  };

  std::vector<std::vector<Distance>> distances;
  size_t row_size;

  DistanceMap(const Points& points) {
    distances.resize(points.size());
    for (size_t i = 0; i < points.size(); ++i) {
      distances[i].resize(points.size());
      for (size_t j = 0; j < points.size(); ++j) {
        distances[i].push_back({sqd(points[i], points[j]), points[j]});
      }
      auto compare_distance = [](const Distance& a, const Distance& b) {
                                return a.distance < b.distance;
                              };
      std::sort(distances[i].begin(), distances[i].end(), compare_distance);
    }
  }

  Range Lookup(uint32_t vid, uint32_t lb, uint32_t ub) {
    const auto& d = distances[vid];
    Range range;
    range.size = 0;
    range.start = nullptr;
    for (size_t i = 0; i < d.size(); ++i) {
      if (d[i].distance < lb) {
        continue;
      }
      if (d[i].distance > ub) {
        break;
      }
      if (range.start == nullptr) {
        range.start = &d[i];
      }
      range.size++;
    }
    return range;
  }
};

uint32_t MinDistance(const Point& p, const Points& points) {
  uint32_t min_distance = 20000000;
  for (const auto& v : points) {
    const uint32_t d = sqd(p, v);
    if (d < min_distance) {
      min_distance = d;
    }
  }
  return min_distance;
}

uint32_t Dislikes(const Problem& problem, const Points& pose) {
  const auto& hole = problem.hole;
  uint32_t sum = 0;
  for (const auto& h : hole) {
    sum += MinDistance(h, pose);
  }
  return sum;
}

bool PointInPolygon(const Point& p, const Points& poly) {
  bool inside = false;
  for (size_t i = 0; i < poly.size(); ++i) {
    size_t j = (i+1)%poly.size();
    const Point& v0 = poly[i];
    const Point& v1 = poly[j];
    if ((v0.y <= p.y) && (v1.y > p.y) || (v1.y <= p.y) && (v0.y > p.y)) {
      double cross = (v1.x - v0.x) * (p.y - v0.y) / (v1.y - v0.y) + v0.x;
      if (cross < p.x) {
        inside = !inside;
      }
    }
  }
  return inside;
}

Points FindAllPointsInHole(const Point& min, const Point& max, const Points& hole) {
  // Now enumerate every point in the bounding box, and if it lies within the
  // polygon, include it.
  //
  // Note: this could be much more efficient, we could combine this with the
  // raycasting in point in polygon and draw one ray for each row, appending
  // points after we flip inside...
  Points points;
  for (int16_t x = min.x; x <= max.x; ++x) {
    for (int16_t y = min.y; y <= max.y; ++y) {
      Point p = {x, y};
      if(PointInPolygon(p, hole)) {
        points.push_back(p);
      }
    }
  }
  return points;
}

Problem ProblemFromJson(const std::string& json_str) {
  Problem problem;
  auto j = json::parse(json_str);

  for (const auto& p : j["figure"]["vertices"]) {
    problem.verts.push_back({p[0], p[1]});
  }
  for (const auto& e : j["figure"]["edges"]) {
    problem.edges.push_back({e[0], e[1]});
  }
  for (const auto& h : j["hole"]) {
    problem.hole.push_back({h[0], h[1]});
  }
  problem.epsilon = j["epsilon"];
  problem.ep = problem.epsilon/1000000.0f;
  std::cout << "ayy " << problem.ep << std::endl;

  // Init original distances
  for (const auto& e : problem.edges) {
    const auto& p1 = problem.verts[e.s];
    const auto& p2 = problem.verts[e.e];
    const float d = sqd(p1, p2);
    problem.original_distances.push_back(d);
  }

  // Find bounding box
  Point min = {30000, 30000};
  Point max = {-30000, -30000};
  for (const auto& h : problem.hole) {
    if (h.x < min.x) {
      min.x = h.x;
    }
    if (h.y < min.y) {
      min.y = h.y;
    }
    if (h.x > max.x) {
      max.x = h.x;
    }
    if (h.y > max.y) {
      max.y = h.y;
    }
  }
  problem.min = min;
  problem.max = max;

  problem.points_in_hole = FindAllPointsInHole(min, max, problem.hole);
  problem.valid_points = std::unordered_set<Point, PointHash>(problem.points_in_hole.begin(),
                                                              problem.points_in_hole.end());

  // Make vert to edge map
  problem.connections.resize(problem.verts.size());
  for (size_t i = 0; i < problem.verts.size(); ++i) {
    for (const auto& e: problem.edges) {
      if (i == e.s) {
        const auto& vs = problem.verts[e.s];
        const auto& ve = problem.verts[e.e];
        problem.connections[i].push_back({e.e, sqd(vs, ve)});
      }
      if (i == e.e) {
        const auto& vs = problem.verts[e.s];
        const auto& ve = problem.verts[e.e];
        problem.connections[i].push_back({e.s, sqd(vs, ve)});
      }
    }
  }

  // Find center
  int sumx = 0;
  int sumy = 0;
  for (const auto& p : problem.points_in_hole) {
    sumx += p.x;
    sumy += p.y;
  }
  sumx /= problem.points_in_hole.size();
  sumy /= problem.points_in_hole.size();
  problem.center = {static_cast<int16_t>(sumx), static_cast<int16_t>(sumy)};

  return problem;
}

enum class PointOrientation {
  LEFT,
  RIGHT,
  COLINEAR,
};

int Area2(const Point& a, const Point& b, const Point& c) {
  return (b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y);
}

// Mad propz to the geniuses at:
// https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
PointOrientation orientation(const Point& a, const Point& b, const Point& c) {
  int area = Area2(a, b, c);
  if (area > 0) {
    return PointOrientation::LEFT;
  }
  if (area < 0) {
    return PointOrientation::RIGHT;
  }
  return PointOrientation::COLINEAR; // a == 0
}

bool SegmentsIntersect(const Point& p1, const Point& p2, const Point& p3, const Point& p4) {
  auto o1 = orientation(p1, p2, p3);
  auto o2 = orientation(p1, p2, p4);
  auto o3 = orientation(p3, p4, p1);
  auto o4 = orientation(p3, p4, p2);

  // We are actually OK with a point being on the boundary
  if (o1 == PointOrientation::COLINEAR) {
    return false;
  }
  if (o2 == PointOrientation::COLINEAR) {
    return false;
  }
  if (o3 == PointOrientation::COLINEAR) {
    return false;
  }
  if (o4 == PointOrientation::COLINEAR) {
    return false;
  }

  if ((o1 != o2) && (o3 != o4)) {
    return true;
  }

  return false;
}

bool SegmentIntersectsHole(const Points& hole, const Point& p1, const Point& p2) {
  for (size_t i = 0; i < hole.size(); ++i) {
    const int j = (i+1)%hole.size();
    const Point& p3 = hole[i];
    const Point& p4 = hole[j];
    if (SegmentsIntersect(p1, p2, p3, p4)) {
      return true;
    }
  }
  return false;
}

bool IsPoseValid(const Problem& problem, const Points& pose) {
  for (const auto& p : pose) {
    if (problem.valid_points.count(p) == 0) {
      // std::cout << "invalid because point not allowed" << std::endl;
      return false;
    }
  }
  for (int i = 0; i < problem.edges.size(); ++i) {
    const Edge& e = problem.edges[i];
    const Point& p1 = pose[e.s];
    const Point& p2 = pose[e.e];

    // Ensure within bounds
    if (SegmentIntersectsHole(problem.hole, p1, p2)) {
      // std::cout << "invalid because segment hits hole" << std::endl;
      return false;
    }

    // Check stretchy factor
    float new_d = sqd(p1, p2);
    float old_d = problem.original_distances[i];
    float stretch = std::abs(new_d/old_d - 1.0f);
    if (stretch >= problem.ep) {
      // std::cout << "invalid because too much stretch:" << std::endl;
      // std::cout << string_format("  edge (%d, %d) -> (%d, %d) was %f but is now %f for a stretch of %f", p1.x, p1.y, p2.x, p2.y, old_d, new_d, stretch) << std::endl;
      return false;
    }

  }
  return true;
}

struct Canvas {
  SDL_Window* window;
  SDL_Renderer* renderer;
  int px_size;
  int bb_size;

  Vec p2px(const Vec& v) {
    const float scale = ((float)px_size)/bb_size;
    return {(v.x+1)*scale, (v.y+1)*scale};
  }
  Vec p2px(const Point& p) {
    const float scale = ((float)px_size)/bb_size;
    return {(p.x+1)*scale, (p.y+1)*scale};
  }
  Vec f2px(const Vec& v) {
    const float scale = ((float)px_size)/bb_size;
    return {(v.x)*scale, (v.y)*scale};
  }

  void DrawFrame(const Points& poly, const Points& qpose,
                 const std::vector<Vec>& pose,
                 const std::vector<Edge>& edges,
                 const std::vector<Force>& forces) {
    // Clear to bg color
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE);
    SDL_RenderClear(renderer);

    // Draw polygon in green
    SDL_SetRenderDrawColor(renderer, 0, 255, 0, SDL_ALPHA_OPAQUE);
    for (int i = 0; i < poly.size(); ++i) {
      int j = (i+1)%poly.size();
      auto p1 = p2px(poly[i]);
      auto p2 = p2px(poly[j]);
      // std::cout << "Poly pt (" << poly[i].x << "," << poly[i].y << ")"
      //           << " -> (" << p1.x << "," << p1.y << ")" << std::endl;
      SDL_RenderDrawLine(renderer, p1.x, p1.y, p2.x, p2.y);
    }

    // Draw pose in red
    SDL_SetRenderDrawColor(renderer, 255, 0, 0, SDL_ALPHA_OPAQUE);
    for (int i = 0; i < edges.size(); ++i) {
      const auto& e = edges[i];
      auto p1 = p2px(pose[e.s]);
      auto p2 = p2px(pose[e.e]);
      SDL_RenderDrawLine(renderer, p1.x, p1.y, p2.x, p2.y);
    }

    // Draw qpose in blue
    SDL_SetRenderDrawColor(renderer, 0, 0, 255, SDL_ALPHA_OPAQUE);
    for (int i = 0; i < edges.size(); ++i) {
      const auto& e = edges[i];
      auto p1 = p2px(qpose[e.s]);
      auto p2 = p2px(qpose[e.e]);
      SDL_RenderDrawLine(renderer, p1.x, p1.y, p2.x, p2.y);
    }

    // Draw forces in white
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, SDL_ALPHA_OPAQUE);
    for (int i = 0; i < pose.size(); ++i) {
      auto p1 = p2px(pose[i]);
      auto f = f2px(forces[i].net);
      Vec p2 = {p1.x + f.x, p1.y + f.y};

      SDL_Rect r;
      int mag = std::sqrt(forces[i].total*10);
      if (mag < 2) {
        mag = 2;
      }
      r.x = p1.x-mag/2;
      r.y = p1.y-mag/2;
      r.w = mag;
      r.h = mag;
      SDL_RenderFillRect(renderer, &r);

      SDL_RenderDrawLine(renderer, p1.x, p1.y, p2.x, p2.y);
    }


    // Update screen
    SDL_RenderPresent(renderer);

    // Give us time to see the frame.
    SDL_Event event;
    bool done = false;
    while (!done) {
      while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) {
          SDL_Quit();
          exit(EXIT_FAILURE);
        }
        if (event.type == SDL_KEYDOWN) {
          done = true;
        }
      }
      SDL_Delay(50);
    }
  }
};

std::unique_ptr<Canvas> MakeCanvas(int bb_size, int px_size) {
  auto canvas = std::make_unique<Canvas>();
  canvas->px_size = px_size;
  canvas->bb_size = bb_size;

  // Create the window where we will draw.
  canvas->window = SDL_CreateWindow("ayylmao",
                  SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                  px_size, px_size,
                  0);

  // We must call SDL_CreateRenderer in order for draw calls to affect this window.
  canvas->renderer = SDL_CreateRenderer(canvas->window, -1, 0);

  return canvas;
}

struct Annealer {
  float nudge_factor;
  int budget;
  Vec wind;
  std::unique_ptr<Solution> solution;

  Annealer(float f, int b) : nudge_factor(f), budget(b), solution(nullptr), wind({0.0f, 0.0f}) {}
};

Force ComputeForce(const Problem& problem,
                   const std::vector<Vec>& pose,
                   const Points& qpose,
                   Annealer& a,
                   uint32_t vid) {
  Force force = {{0.0f, 0.0f}, 0.0f};
  force.net.x += a.wind.x;
  force.net.y += a.wind.y;
  force.total += a.wind.mag();

  const auto& connections = problem.connections[vid];
  const Vec& v1 = pose[vid];
  const Point& p1 = qpose[vid];

  // Each connection exerts a force corresponding to stretch factor.
  for (const auto& con : connections) {
    const Vec& v2 = pose[con.other];
    const Point& p2 = qpose[con.other];
    // float stretch = sqd(p1, p2)/con.distance - 1.0f;
    // if (-problem.ep < stretch && stretch < problem.ep) {
    //   stretch = 0.0f;
    // }
    float new_d = sqd(p1, p2);
    float old_d = con.distance;
    float stretch = new_d/old_d - 1.0f;
    if (std::abs(stretch) < problem.ep) {
      stretch = 0.0f;
    }

    Vec direction = {v2.x - v1.x, v2.y - v1.y};
    if (direction.x == 0.0f && direction.y == 0.0f) {
      int hid = vid%problem.hole.size();
      direction = {problem.hole[hid].x - v1.x, problem.hole[hid].y - v1.y};
    }
    direction = direction.norm();
    force.net.x += direction.x*stretch;
    force.net.y += direction.y*stretch;
    force.total += stretch;


    float randx = 0.01f*(rand()%100 - 50);
    float randy = 0.01f*(rand()%100 - 50);
    force.net.x += randx;
    force.net.y += randy;
    // force.total += stretch;

    if (SegmentIntersectsHole(problem.hole, v1.quantize(), v2.quantize())) {
      Vec to_center = {problem.center.x - v1.x, problem.center.y - v1.y};
      // force.x += to_center.x;
      // force.y += to_center.y;
      float wigglex = 0.1f*(rand()%100 - 50);
      float wiggley = 0.1f*(rand()%100 - 50);
      force.net.x += wigglex;
      force.net.y += wiggley;
    }
  }

  // If we're outside the hole, try to come back in
  if (!PointInPolygon(p1, problem.hole)) {
    Vec to_center = {problem.center.x - v1.x, problem.center.y - v1.y};
    force.net.x += 10.0f*to_center.x;
    force.net.y += 10.0f*to_center.y;
    force.total += to_center.mag();
  }

  force.net = force.net.cronch();
  // if (force.mag() > 10) {
  //   std::cout << "wtf, big force (" << force.x << ", " << force.y << ")" << std::endl;
  // }
  return force;
}

void UpdateForces(const Problem& problem,
                  const std::vector<Vec>& pose,
                  const Points& qpose,
                  Annealer& a,
                  std::vector<Force>& forces) {
  for (size_t i = 0; i < pose.size(); ++i) {
    auto force = ComputeForce(problem, pose, qpose, a, i);
    forces[i] = force;
  }
}

Vec NewWind() {
  float randx = 0.1f*(rand()%10 - 5);
  float randy = 0.1f*(rand()%10 - 5);
  return {randx, randy};
}

void Anneal(const Problem& problem, Annealer& a, Canvas* canvas) {
  // Lay out initial pose
  std::vector<Vec> pose;
  Points qpose;

  a.wind = NewWind();

  for (const auto& p : problem.verts) {
    // std::cout << "Initial vert (" << p.x << "," << p.y << ")" << std::endl;
              // << " -> (" << p1.x << "," << p1.y << ")" << std::endl;

    // pose.push_back({(float)p.x, (float)p.y});
    // qpose.push_back(p);

    // const int random_idx = rand()%problem.points_in_hole.size();
    // const Point& rp = problem.points_in_hole[random_idx];
    // pose.push_back({(float)rp.x, (float)rp.y});
    // qpose.push_back(rp);

    const int random_idx = rand()%problem.hole.size();
    const Point& rp = problem.hole[random_idx];
    pose.push_back({(float)rp.x, (float)rp.y});
    qpose.push_back(rp);

    //pose.push_back({(float)problem.center.x, (float)problem.center.y});
    //qpose.push_back(problem.center);
  }

  // Keep all forces, for drawing the debug view
  std::vector<Force> forces;
  forces.resize(problem.verts.size());

  UpdateForces(problem, pose, qpose, a, forces);

  // Maybe draw for debugging
  if (canvas != nullptr) {
    canvas->DrawFrame(problem.hole, problem.verts, pose, problem.edges, forces);
  }

  // Iterate until tries exhausted
  while (a.budget-- != 0) {
    // Update wind periodically
    if (a.budget%1000 == 0) {
      a.wind = NewWind();
    }

    // Apply forces
    for (size_t i = 0; i < pose.size(); ++i) {
      const auto& force = forces[i];
      // std::cout << string_format("nudged (%f, %f)", pose[i].x, pose[i].y);
      const float net_mag = force.net.mag();
      if (force.total > 10.0f*net_mag && net_mag < 0.05f) {
        const int random_idx = rand()%problem.hole.size();
        const Point& rp = problem.hole[random_idx];
        pose[i].x = rp.x;
        pose[i].y = rp.y;
      } else {
        pose[i].x += a.nudge_factor*force.net.x;
        pose[i].y += a.nudge_factor*force.net.y;
      }
      // std::cout << string_format("--> (%f, %f)", pose[i].x, pose[i].y) << std::endl;
      qpose[i] = pose[i].quantize();
    }

    // Compute next forces
    UpdateForces(problem, pose, qpose, a, forces);

    // Maybe draw for debugging
    if (canvas != nullptr) {
      canvas->DrawFrame(problem.hole, qpose, pose, problem.edges, forces);
    }

    // Check if the pose is valid, and if so, report it as a solution
    if (IsPoseValid(problem, qpose)) {
      const uint32_t dislikes = Dislikes(problem, qpose);
      a.solution = std::make_unique<Solution>();
      *a.solution = {dislikes, std::move(qpose)};
      return;
    }
  }
}

std::unique_ptr<Solution> Anneal(const Problem& problem, Canvas* canvas) {
  Annealer a(0.80f, 10000000);
  Anneal(problem, a, canvas);

  if (a.solution) {
    std::cout << "ayy lmao" << std::endl;
    std::cout << "dislikes: " << a.solution->dislikes << std::endl;
  } else {
    std::cout << "so sad can I get a like" << std::endl;
  }
  return std::move(a.solution);
}

std::unique_ptr<Solution> Search(const Problem& problem, int num_threads, int iterations) {
  std::unique_ptr<Solution> best;

  for (int i = 0; i < iterations; ++i) {
    std::vector<Annealer> annealers;
    std::vector<std::thread> threads;

    annealers.reserve(num_threads);
    threads.reserve(num_threads);
    for (int t = 0; t < num_threads; ++t) {
      annealers.emplace_back(0.05f, 100000);
      Annealer* a = &annealers[t];
      threads.emplace_back([&problem, a] {
                             Anneal(problem, *a, nullptr);
                           }
      );
    }
    for (int t = 0; t < num_threads; ++t) {
      threads[t].join();
      if (annealers[t].solution) {
        // std::cout << "ayy lmao worker " << t
        //           << " found a solution, dislikes: "
        //           << annealers[t].solution->dislikes << std::endl;
        if (!best || best->dislikes > annealers[t].solution->dislikes) {
          std::cout << "new best solution, dislikes: "
                    << annealers[t].solution->dislikes << std::endl;
          best = std::move(annealers[t].solution);
        }
      } else {
        // std::cout << "worker " << t
        //           << " has FAILED US, WHY HAS GOD FORSAKEN US" << std::endl;
      }
    }
  }

  return best;
}

std::string ReadFile(const char* fname) {
  std::ifstream t(fname);
  std::string str((std::istreambuf_iterator<char>(t)),
                  std::istreambuf_iterator<char>());
  return str;
}

json SolutionToJson(const Solution& s) {
  json j;
  j["vertices"] = json::array();
  for (int i = 0; i < s.assigned.size(); ++i) {
    const auto& p = s.assigned[i];
    j["vertices"].push_back(json::array());
    j["vertices"][i].push_back(p.x);
    j["vertices"][i].push_back(p.y);
  }
  return j;
}

void DoMain(const std::vector<int>& problems, int threads, int generations) {
  for (int problem_id : problems) {
    std::string json_str = GetProblem(problem_id);
    auto problem = ProblemFromJson(json_str);
    auto best = Search(problem, threads, generations);
    if (best) {
      std::cout << "Best solution for problem " << problem_id << " has "
                << best->dislikes << " dislikes" << std::endl;
      json j = SolutionToJson(*best);;
      const auto data = j.dump();
      std::cout << "POST: " << data << std::endl;
      std::cout << SubmitProblem(problem_id, data) << std::endl;
    }
  }
}

int main(int argc, char** argv) {
  srand(time(nullptr));

  bool sdl = false;
  bool dolist = false;
  const char* fname;
  if (argc == 3) {
    if (argv[1][0] == 'd') {
      sdl = true;
    }
    fname = argv[2];
  }
  if (argc == 2) {
    fname = argv[1];
  }
  if (argc == 4) {
    int threads = atoi(argv[1]);
    int generations = atoi(argv[2]);
    auto problems = parse_csv(argv[3]);
    DoMain(problems, threads, generations);
    return 0;
  }

  //auto json_str = ReadFile(fname);
  std::string json_str;
  json_str = ReadFile(fname);

  auto problem = ProblemFromJson(json_str);

  auto bb_largest_side_plus_padding = std::max(problem.max.x, problem.max.y) + 2;

  if (sdl) {
    // Initialize SDL.
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
      return 1;
    }
    auto canvas = MakeCanvas(bb_largest_side_plus_padding, 1024);
    Anneal(problem, canvas.get());
    SDL_Quit();
    return 0;
  }

  auto best = Search(problem, 8, 20);
  if (best) {
    std::cout << "Best solution has " << best->dislikes << " dislikes" << std::endl;

    json j = SolutionToJson(*best);;

    std::ofstream file("/tmp/solution.json");
    file << j;
  }

  return 0;
}
