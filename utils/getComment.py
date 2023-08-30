
from typing import Any, Dict
from specklepy.api.client import SpeckleClient
from gql import gql

def get_comments(
    client: SpeckleClient,
    project_id: str,
) -> Dict[str, Any]:
    return client.httpclient.execute(
        gql("""
            query c{
            comments(streamId:"17b0b76d13")
                {
                    items {
                    id
                    rawText
                    viewerState
                    }
                }
            }
            """
        )
    )