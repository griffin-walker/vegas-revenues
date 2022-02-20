# install.packages(c("tidyverse", "reshape2", "knitr", "kableExtra")) # necessary dependencies
library(ggplot2)
library(tidyverse)
library(reshape2)
library(knitr)
library(kableExtra)
library(scales)


data_path = "cleaned_vegas_revenues.csv"
# load data from vegas-revenues python code
df <- read.csv(data_path)
# create/ convert some date cols
df$year_month <- as.Date(paste0(df$year_month, "/01"), format = "%Y/%m/%d")
df$year <- lubridate::year(df$year_month)

# define color scheming
substack_page_background = "#F5FCFF"
substack_page_accent = "#5465D1"
grey_text_color = "#282828"

# define substack theme for charts
substack_theme <- theme(
  panel.background = element_rect(
    fill = substack_page_background,
    colour = substack_page_background,
    size = 0.5,
    linetype = "solid"
  ),
  panel.grid.major = element_line(colour = substack_page_background),
  panel.grid.minor = element_line(colour = substack_page_background),
  plot.background = element_rect(fill = substack_page_background),
  axis.text = element_text(color = grey_text_color, size = 10),
  axis.title = element_text(color = grey_text_color, size = 12)
)

# plot total monthly revenues (2004 - present)
total_monthly_revenues_ts_plot <- ggplot(data = df) +
  geom_point(aes(x = year_month, y = total, colour = "Total"), size = 1) +
  geom_line(aes(x = year_month, y = total, colour = "Total"), alpha = 0.3) +
  geom_smooth(
    aes(x = year_month, y = total, colour = "Total"),
    method = "loess",
    span = 0.12,
    se = F
  ) +
  scale_color_manual(values = substack_page_accent) +
  scale_x_date(date_breaks = "years", date_labels = "%Y") +
  scale_y_continuous(labels = scales::dollar) +
  xlab("Year") +
  ylab("Monthly Revenue (Total)") +
  substack_theme +
  theme(legend.position = "none") # we don't care about a legend here

# plot monthly revenues for slots and tables (2004 - present)
slots_vs_table_revenues_ts_plot <- ggplot(data = df) +
  geom_point(aes(x = year_month, y = slots_total, colour = "Slots"), size = 1) +
  geom_line(aes(x = year_month, y = slots_total, colour = "Slots"), alpha = 0.3) +
  geom_smooth(
    aes(x = year_month, y = slots_total, colour = "Slots"),
    method = "loess", span = 0.12, se = F
  ) +
  geom_point(aes(x = year_month, y = tables_total, colour = "Tables"), size = 1) +
  geom_line(aes(x = year_month, y = tables_total, colour = "Tables"), alpha = 0.3) +
  geom_smooth(
    aes(x = year_month, y = tables_total, colour = "Tables"),
    method = "loess", span = 0.12, se = F
    ) +
  scale_color_manual(values = c("#F8A848", "#226216"), name = "Gaming Type") +
  scale_x_date(date_breaks = "years", date_labels = "%Y") +
  scale_y_continuous(labels = scales::dollar) +
  xlab("Year") +
  ylab("Monthly Revenue (Total)") +
  substack_theme


# aggregate yearly table game revenues 
table_agg <- df %>%
  group_by(year) %>%
  summarise(
    Craps = sum(tables_craps),
    Roulette = sum(tables_roulette),
    Blackjack = sum(tables_twenty_one),
    Baccarat = sum(tables_baccarat)
  )
table_agg$year <- lubridate::year(as.Date(paste0(table_agg$year, "/01/01"), "%Y/%m/%d"))
table_agg <- melt(table_agg, id.vars = "year") # melt the data for ggplot to auto plot the categories


# plot annual revenues for table games (side by side bar plot)
annual_table_game_revenues_ts_plot <- 
  ggplot(data = table_agg, aes(x = factor(year), y = value, fill = variable)) +
  geom_bar(stat = "identity",
           position = "dodge",
           width = 0.9) +
  scale_fill_manual(values = c("#FFC107", "#004D40", "#D81B60", "#1E88E5"),
                    name = "Gaming Type") +
  scale_y_continuous(labels = scales::dollar) +
  scale_x_discrete() +
  xlab("Year") +
  ylab("Yearly Revenue (per table game)") +
  substack_theme +
  theme(
    legend.position = c(0.94, 0.85), # put the legend in the top right
    legend.text = element_text(size = 12),
    legend.title = element_text(size = 12)
  )


# aggregate annual slot revenues 
slots_agg <- df %>%
  group_by(year) %>%
  summarise(
    one_cent_sum = sum(slots_1_cent),
    five_cent_sum = sum(slots_5_cent),
    twenty_five_cent_sum = sum(slots_25_cent),
    one_dollar_sum = sum(slots_1_dollar),
    five_dollar_sum = sum(slots_5_dollar),
    twenty_five_dollar_sum = sum(slots_25_dollar),
    hundred_dollar_sum = sum(slots_100_dollar),
    multi_denomination_sum = sum(slots_multi_denomination),
    slots_sum = sum(slots_total)
  ) %>%
  mutate(
    one_cent_p = one_cent_sum / slots_sum,
    five_cent_p = five_cent_sum / slots_sum,
    twenty_five_cent_p = twenty_five_cent_sum / slots_sum,
    one_dollar_p = one_dollar_sum / slots_sum,
    five_dollar_p = five_dollar_sum / slots_sum,
    twenty_five_dollar_p = twenty_five_dollar_sum / slots_sum,
    hundred_dollar_p = hundred_dollar_sum / slots_sum,
    multi_denomination_p = multi_denomination_sum / slots_sum,
    total_p = slots_sum / slots_sum,
  )


# get median annual percentages for slot types
slots_summary <- t(
  slots_agg[slots_agg$year < 2020,] %>%
    summarise(
      `One Cent` = median(one_cent_p),
      `Five Cent` = median(five_cent_p),
      `Twenty Five Cent` = median(twenty_five_cent_p),
      `One Dollar` = median(one_dollar_p),
      `Five Dollar` = median(five_dollar_p),
      `Twenty Five Dollar` = median(twenty_five_dollar_p),
      `Hundred Dollar` = median(hundred_dollar_p),
      `Multi-denomination` = median(multi_denomination_p),
      `Total` = 0 # this stat doesn't make sense, let's just fill
    )
)

# dataframe clean up 
slots_summary <- as.data.frame(slots_summary)
slots_summary$stat <- row.names(slots_summary)
row.names(slots_summary) <- 1:nrow(slots_summary)
names(slots_summary) <- c("Median Annual Revenue Percentage", "Slot Type")
slots_summary <- slots_summary[, c(2, 1)] # swap column order
slots_summary$`Median Annual Revenue Percentage` <- percent(round(slots_summary$`Median Annual Revenue Percentage`, 4))
slots_summary[nrow(slots_summary), 2] <- "-"

# calculate median annual revenues for slot types
median_annual_slot_type_revenues <-
  as.data.frame(t(
    slots_agg[slots_agg$year < 2020,] %>%
      summarise(
        median(one_cent_sum),
        median(five_cent_sum),
        median(twenty_five_cent_sum),
        median(one_dollar_sum),
        median(five_dollar_sum),
        median(twenty_five_dollar_sum),
        median(hundred_dollar_sum),
        median(multi_denomination_sum),
        median(slots_sum)
      )
  ))$V1

# cbind data
slots_summary$`Median Annual Revenue Sum` <- dollar(median_annual_slot_type_revenues)

# generate html table 
slots_summary_table <- slots_summary %>%
  kbl(align=c('l', 'r', 'r')) %>%
  kable_styling(bootstrap_options = c("striped", "hover")) %>%
  row_spec(0:nrow(slots_summary), background = substack_page_background)


#### Let's see everything
total_monthly_revenues_ts_plot
slots_vs_table_revenues_ts_plot
annual_table_game_revenues_ts_plot
slots_summary_table