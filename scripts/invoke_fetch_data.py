import typer

from solar_predictor.handlers.fetch_data import lambda_handler


def main(
    lat: float = typer.Option(..., help="Latitude"),
    long: float = typer.Option(..., help="Longitude"),
    start_date: str | None = typer.Option(None, help="YYYY-MM-DD"),
    end_date: str | None = typer.Option(None, help="YYYY-MM-DD"),
):
    event = {
        "lat": lat,
        "long": long,
        "start_date": start_date,
        "end_date": end_date,
    }
    res = lambda_handler({k: v for k, v in event.items() if v is not None}, {})
    print(res)


if __name__ == "__main__":
    typer.run(main)
