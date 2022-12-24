from __future__ import annotations

import datetime
import time
from typing import Optional

from selenium import webdriver

from sunbottle.data.sharp import constants as sharp_constants
from sunbottle.domain.electricity import generation
from sunbottle.domain.sharp import operations as sharp_ops

from . import queries


class SharpGenerationRetriever(generation.GenerationRetriever):
    def retrieve(
        self,
        browser: Optional[webdriver.Firefox] = None,
        date: Optional[datetime.date] = None,
    ) -> list[generation.GenerationReading]:
        if not browser:
            raise ValueError("Browser is required to retrieve generation data")

        # Ensure we're logged in.
        try:
            sharp_ops.login_browser(browser, url=sharp_constants.GENERATION_URL)
        except sharp_ops.AlreadyLoggedIn:
            pass
        else:
            time.sleep(self._sleep_time())

        if date:
            time.sleep(self._sleep_time())
            self._select_date(browser, date)
            time.sleep(self._sleep_time())

        generation_data = None

        for attempt in range(1, 5):
            try:
                generation_data = browser.execute_script("return onRenderResult.object")
            except Exception:
                print("Failed to get generation data. Waiting before trying again.")
                time.sleep(attempt * 5)
            else:
                print("Fetched generation data.")
                break

        if generation_data is None:
            return []
        return queries.sharp_generation_to_reading(generation_data, date)

    def _select_date(self, browser: webdriver.Firefox, date: datetime.date) -> None:
        select_script = """
        var param = {
            "pageAction": "changePage",
            "displayDate": "%s",
            "displaySpan": "daily"
        }
        onReadyJson.sendJsonNoDialog("A121641000.htm", param, function(response, resultJson) {
            if(response) {
            // 処理OK時の処理
                checkCalValBtn = 0;
            location.href = "A121641000.htm";
            } else {
            // 処理NG時の処理
                openAlert(escapeCharacter(resultJson.errMsg), "OK", function(){
                    setTimeout(function () {location.replace("A121000000.htm");}, 1);
                });
            }
        });""" % date.strftime(
            "%Y/%m/%d"
        )
        browser.execute_script(select_script)

    def _sleep_time(self) -> int:
        return 5
