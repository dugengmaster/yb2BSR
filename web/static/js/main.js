
function redirectToLineLogin() {
    window.location.href = "{% url 'custom_line_login' %}";
}

// food.html 操作地圖
function initMap_food() {
    // 創建地圖
    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 25.0330, lng: 121.5654}, // 預設中心為台北市
        zoom: 13
    });

    // 創建搜索框並將其綁定到 UI 元素
    var input = document.getElementById('pac-input');
    var searchBox = new google.maps.places.SearchBox(input);

    // 偵聽搜索框的結果並設置地圖的邊界
    map.addListener('bounds_changed', function() {
        searchBox.setBounds(map.getBounds());
    });

    var markers = [];

    // 偵聽搜索框的地點選擇事件
    searchBox.addListener('places_changed', function() {
        var places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }

        // 清除舊的地標
        markers.forEach(function(marker) {
            marker.setMap(null);
        });
        markers = [];

        // 獲取地點的邊界
        var bounds = new google.maps.LatLngBounds();
        places.forEach(function(place) {
            if (!place.geometry) {
                console.log("Returned place contains no geometry");
                return;
            }

            // 創建地標
            var marker = new google.maps.Marker({
                map: map,
                title: place.name,
                position: place.geometry.location
            });
            markers.push(marker);

            if (place.geometry.viewport) {
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
        map.fitBounds(bounds);
    });
}

// 點擊以顯示或隱藏 description
function toggleDescription(element) {
    var description = element.querySelector('.description');
    var isVisible = description.style.display === 'block';


    document.querySelectorAll('.card .description').forEach(function(desc) {
        desc.style.display = 'none';
    });


    if (!isVisible) {
        description.style.display = 'block';
    } else {
        description.style.display = 'none';
    }
}

// 顯示對應城市的圖表
function showChart(city) {
    cityChart.data.datasets[0].data = cityData[city];
    cityChart.data.datasets[0].label = `${city}騎腳踏車人數`;
    cityChart.update();
}

// bike.html
function openModal(trailId) {
    const trail = trails[trailId];
    const modal = new bootstrap.Modal(document.getElementById('trailModal'));
    document.getElementById('trailModalLabel').innerText = trail.title;
    document.querySelector('#trailModal .modal-body').innerHTML = `
        <p>${trail.description}</p>
        <p>${trail.scenicSpots}</p>
        <p>${trail.estimatedTime}</p>
        <p>${trail.difficulty}</p>
        <div class="star-rating">
            ${renderStars(trail.rating)}
        </div>
        <textarea class="form-control mt-3" id="userComment" placeholder="留下您的意見與評語"></textarea>
    `;
    modal.show();
}

function renderStars(rating) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= rating) {
            stars += '<i class="fas fa-star checked"></i>';
        } else if (i === Math.ceil(rating)) {
            stars += '<i class="fas fa-star-half-alt checked"></i>';
        } else {
            stars += '<i class="fas fa-star"></i>';
        }
    }
    return stars;
}