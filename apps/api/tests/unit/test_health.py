from trustlayer.main import create_app


def test_create_app_exposes_health_route() -> None:
    app = create_app()

    route_paths = {route.path for route in app.routes}

    assert "/health" in route_paths
