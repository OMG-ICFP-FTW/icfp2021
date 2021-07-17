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

#include <xmmintrin.h>

// #include <SDL.h>
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

using Points = std::vector<Point>;

struct Edge {
  uint32_t s;
  uint32_t e;
};

struct Vec {
  float x;
  float y;
};

struct Problem {
  Points verts;
  Points hole;

  std::vector<Edge> edges;

  uint32_t epsilon;
  float ep;

  // List of all points that lie within the hole.
  Points points_in_hole;
  std::unordered_set<Point, PointHash> valid_points;

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

constexpr uint8_t LEFT = 0;
constexpr uint8_t RIGHT = 1;
constexpr uint8_t COLINEAR = 2;

// Mad propz to the geniuses at:
// https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
static inline uint8_t orientation(int area) {
  if (area > 0) {
    return LEFT;
  }
  if (area < 0) {
    return RIGHT;
  }
  return COLINEAR; // a == 0
}

static inline bool SegmentsIntersectSimd(const Point& p1, const Point& p2,
                                         const Point& p3, const Point& p4) {
  // Create 4 vectors to compute signed areas all at once, according to:
  // auto o1 = orientation(p1, p2, p3);
  // auto o2 = orientation(p1, p2, p4);
  // auto o3 = orientation(p3, p4, p1);
  // auto o4 = orientation(p3, p4, p2);
  __m128i Ax = _mm_set_epi32(p1.x, p1.x, p3.x, p3.x);
  __m128i Ay = _mm_set_epi32(p1.y, p1.y, p3.y, p3.y);
  __m128i Bx = _mm_set_epi32(p2.x, p2.x, p4.x, p4.x);
  __m128i By = _mm_set_epi32(p2.y, p2.y, p4.y, p4.y);
  __m128i Cx = _mm_set_epi32(p3.x, p4.x, p1.x, p2.x);
  __m128i Cy = _mm_set_epi32(p3.y, p4.y, p1.y, p2.y);

  // Compute signed area:
  // (b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y);
  __m128i t0 = _mm_mullo_epi32(_mm_sub_epi32(Bx, Ax), _mm_sub_epi32(Cy, Ay));
  __m128i t1 = _mm_mullo_epi32(_mm_sub_epi32(Cx, Ax), _mm_sub_epi32(By, Ay));
  __m128i area = _mm_sub_epi32(t0, t1);

  const int o1 = orientation(_mm_extract_epi32(area, 3));
  const int o2 = orientation(_mm_extract_epi32(area, 2));
  const int o3 = orientation(_mm_extract_epi32(area, 1));
  const int o4 = orientation(_mm_extract_epi32(area, 0));


  // We are actually OK with a point being on the boundary
  if (o1 == COLINEAR) {
    return false;
  }
  if (o2 == COLINEAR) {
    return false;
  }
  if (o3 == COLINEAR) {
    return false;
  }
  if (o4 == COLINEAR) {
    return false;
  }

  if ((o1 != o2) && (o3 != o4)) {
    return true;
  }

  return false;
}

static inline bool SegmentIntersectsHoleSimd(const Points& hole, const Point& p1, const Point& p2) {
  for (size_t i = 0; i < hole.size(); ++i) {
    const int j = (i+1)%hole.size();
    const Point& p3 = hole[i];
    const Point& p4 = hole[j];
    if (SegmentsIntersectSimd(p1, p2, p3, p4)) {
      return true;
    }
  }
  return false;
}

void DisplayProgress(uint64_t done, uint64_t total) {
  constexpr int barWidth = 70;

  double progress = ((double)done)/total;;
  std::cout << "[";
  int pos = barWidth * progress;
  for (int i = 0; i < barWidth; ++i) {
    if (i < pos) std::cout << "=";
    else if (i == pos) std::cout << ">";
    else std::cout << " ";
  }
  std::cout << "] " << done << "/" << total << "("
            << int(progress * 100.0) << " %)\r";
  std::cout.flush();
}

void GenerateForbiddenEdges(const std::string& fname, const Problem& problem) {
  std::ofstream f(fname, std::ios::app | std::ios::binary);

  const size_t size = problem.points_in_hole.size();
  const uint64_t total = size*size;
  const uint64_t meaningful_increment = total >= 1000 ? total/1000 : 100;

  uint64_t done = 0;
  for (const auto& p1 : problem.points_in_hole) {
    for (const auto& p2: problem.points_in_hole) {
      const bool intersects = SegmentIntersectsHoleSimd(problem.hole, p1, p2);
      // const bool old_intersects = SegmentIntersectsHole(problem.hole, p1, p2);
      // // std::cout << string_format("(%d, %d) - (%d, %d) ", p1.x, p1.y, p2.x, p2.y);
      // // std::cout << string_format("%d vs %d", intersects, old_intersects);
      // if (intersects != old_intersects) {
      //   std::cout << " wat" << std::endl;
      //   exit(1);
      // } else {
      //   // std::cout << " ok" << std::endl;
      // }
      if(intersects) {
        f.write(reinterpret_cast<const char*>(&p1.x), sizeof(p1.x));
        f.write(reinterpret_cast<const char*>(&p1.y), sizeof(p1.y));
        f.write(reinterpret_cast<const char*>(&p2.x), sizeof(p2.x));
        f.write(reinterpret_cast<const char*>(&p2.y), sizeof(p2.y));
      }
      done++;
      if (done % meaningful_increment == 0) {
        DisplayProgress(done, total);
      }
    }
  }
  f.close();
}

std::string ReadFile(const char* fname) {
  std::ifstream t(fname);
  std::string str((std::istreambuf_iterator<char>(t)),
                  std::istreambuf_iterator<char>());
  return str;
}

int main(int argc, char** argv) {

  int problem_id = atoi(argv[1]);
  const char* fname = argv[2];

  std::string json_str;
  json_str = ReadFile(fname);

  auto problem = ProblemFromJson(json_str);
  GenerateForbiddenEdges(string_format("/tmp/%d_forbidden_edges.bin", problem_id), problem);

  return 0;
}
